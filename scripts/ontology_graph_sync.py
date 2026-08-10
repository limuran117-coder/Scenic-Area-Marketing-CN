#!/usr/bin/env python3
"""
Ontology M6: 图谱同步钩子（Graph Sync Hook）。

在 ingested 写入 SQLite 后，把新 objects 同步追加到图谱 JSONL（关系查询层）。
设计原则：
- FAIL-OPEN：图谱同步失败绝不影响 SQLite 主流程（SQLite 仍是权威存储）
- 幂等：同 (id, type) 不重复创建；同步前查重
- 只追加：图谱是关系查询层快照，不承担权威，异常时静默跳过

由 scripts/ontology/ontology_store.py 的 ingest_objects 在写入成功后调用。
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_WORKSPACE = Path(__file__).resolve().parent.parent  # workspace/（scripts/ 上一层）
sys.path.insert(0, str(_WORKSPACE / "skills/ontology/scripts"))
sys.path.insert(0, str(_WORKSPACE / "scripts"))

GRAPH_PATH = _WORKSPACE / "wiki/技术配置/Ontology架构设计/graph/graph.jsonl"

# schema → 图谱 type 映射
SCHEMA_TO_TYPE = {
    "MetricSnapshot": "MetricSnapshot",
    "ContentAsset": "ContentAsset",
    "TouristSegment": "TouristSegment",
    "Event": "MarketingCampaign",
    "ScenicSpot": "ScenicSpot",
}


def _existing(graph_path: Path) -> tuple[set, set]:
    """返回 (实体id集合, 关系集合)。读一次全量。"""
    ids, rels = set(), set()
    if not graph_path.exists():
        return ids, rels
    for line in graph_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        op = rec.get("op")
        if op == "create":
            ids.add(rec["entity"]["id"])
        elif op == "relate":
            rels.add((rec.get("from"), rec.get("rel"), rec.get("to")))
    return ids, rels


def _append_op(graph_path: Path, record: dict) -> None:
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    with graph_path.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _build_entity(eid: str, etype: str, props: dict) -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    return {"id": eid, "type": etype, "properties": props, "created": ts, "updated": ts}


def sync_to_graph(schema: str, objects: list[dict]) -> tuple[int, str | None]:
    """
    把本轮写入的 objects 追加到图谱。
    返回 (synced_count, error_message)。error 时返回 (0, msg)，调用方必须 ignore。
    """
    etype = SCHEMA_TO_TYPE.get(schema)
    if not etype:
        return 0, f"schema {schema} 无图谱映射，跳过"
    if not objects:
        return 0, None

    try:
        ids, rels = _existing(GRAPH_PATH)
        synced = 0
        for obj in objects:
            eid = obj.get("id")
            if not eid:
                continue
            # 幂等跳过
            if eid in ids:
                continue
            props = {k: v for k, v in obj.items() if k != "id" and v is not None}
            if etype == "MetricSnapshot":
                # 指标需带 spot_id 关联 → 生成 has_metric 关系
                # 兼容两种字段：SQLite列 spot_id（_map_fields后）或 adapter原始 scenicSpotId
                sid = obj.get("spot_id") or obj.get("scenicSpotId")
                if sid:
                    rel_key = (sid, "has_metric", eid)
                    if rel_key not in rels:
                        _append_op(GRAPH_PATH, {
                            "op": "relate", "from": sid, "rel": "has_metric", "to": eid,
                            "properties": {}, "timestamp": datetime.now(timezone.utc).isoformat()})
                        rels.add(rel_key)
            _append_op(GRAPH_PATH, {"op": "create", "entity": _build_entity(eid, etype, props),
                                    "timestamp": datetime.now(timezone.utc).isoformat()})
            ids.add(eid)
            synced += 1
        return synced, None
    except Exception as e:  # FAIL-OPEN
        return 0, f"graph sync failed (ignored): {e}"[:200]
