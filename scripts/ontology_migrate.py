#!/usr/bin/env python3
"""
Ontology M3: 迁移生产库数据到图谱 JSONL（保留 SQLite 底座）。

融合路径（ADR-001）：用通用图谱引擎 + 景区领域 schema，接回生产数据。
数据源 SLAVE：.profile/ontology/ontology_store.db（只读，不删改）
输出 TARGET：wiki/技术配置/Ontology架构设计/graph/graph.jsonl

用法：
  python3 scripts/ontology_migrate.py            # 全量迁移
  python3 scripts/ontology_migrate.py --dry-run  # 只打印计划不写入

幂等：按业务 ID 去重，重复运行不产生重复实体。
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from pathlib import Path

# 引擎路径
WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE / "skills/ontology/scripts"))
import ontology as eng  # noqa: E402

# 路径
DB_PATH = Path(WORKSPACE) / ".profile/ontology/ontology_store.db"
GRAPH_PATH = Path(WORKSPACE) / "wiki/技术配置/Ontology架构设计/graph/graph.jsonl"
SCHEMA_PATH = Path(WORKSPACE) / "wiki/技术配置/Ontology架构设计/movie-town-schema.yaml"

# 领域常量（ID 单源）—— 与 ontology_constants 对齐
TIER = {
    "movie_town": "secondary", "wansui_mountain": "national",
    "qingming_riverside": "national", "only_henan": "secondary",
    "fangte": "secondary", "haichang": "secondary",
    "yinji": "secondary", "only_dream": "national",
}
NAME_BY_ID = {
    "movie_town": "郑州电影小镇", "wansui_mountain": "万岁山武侠城",
    "qingming_riverside": "清明上河园", "only_henan": "只有河南戏剧幻城",
    "fangte": "郑州方特欢乐世界", "haichang": "郑州海昌海洋公园",
    "yinji": "郑州银基动物王国", "only_dream": "只有红楼梦戏剧幻城",
    "大唐不夜城": "大唐不夜城",
}
CATEGORY = {
    "movie_town": "演艺小镇", "wansui_mountain": "武侠城",
    "qingming_riverside": "水乡古镇", "only_henan": "戏剧幻城",
    "fangte": "乐园", "haichang": "海洋公园", "yinji": "乐园",
    "only_dream": "戏剧幻城", "大唐不夜城": "街区商业",
}


def existing_ids(graph_path: Path) -> set:
    """读已有图谱，返回所有实体 ID 集合（幂等用）。"""
    ids = set()
    if graph_path.exists():
        for line in graph_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("op") == "create":
                ids.add(rec["entity"]["id"])
            elif "entity" in rec:
                ids.add(rec["entity"]["id"])
    return ids


def existing_rels(graph_path: Path) -> set:
    """读已有图谱，返回 (from, rel, to) 关系集合（relate 幂等用）。"""
    rels = set()
    if graph_path.exists():
        for line in graph_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("op") == "relate":
                rels.add((rec.get("from"), rec.get("rel"), rec.get("to")))
    return rels


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印计划不写入")
    args = ap.parse_args()

    if not DB_PATH.exists():
        print(f"❌ 生产库不存在: {DB_PATH}")
        return 1
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    existing = existing_ids(GRAPH_PATH)
    existing_r = existing_rels(GRAPH_PATH)
    created, skipped, rels = [], 0, []

    def emit(entity_id: str, type_name: str, props: dict) -> None:
        nonlocal skipped
        if entity_id in existing:
            skipped += 1
            return
        if args.dry_run:
            print(f"  [计划] create {type_name} {entity_id}")
            return
        existing.add(entity_id)
        eng.create_entity(type_name, props, str(GRAPH_PATH), entity_id)
        created.append(entity_id)

    def emit_rel(frm: str, rel: str, to: str) -> None:
        nonlocal rels
        key = (frm, rel, to)
        if key in existing_r:
            return
        if args.dry_run:
            print(f"  [计划] relate {frm} -{rel}-> {to}")
            return
        existing_r.add(key)
        ts = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        eng.append_op(GRAPH_PATH, {"op": "relate", "from": frm, "rel": rel, "to": to,
                                   "properties": {}, "timestamp": ts})
        rels.append(f"{frm}-{rel}->{to}")

    # 1. ScenicSpot（8 个，稳定业务 ID）
    print("=== M3 迁移: ScenicSpot ===")
    spots = {r["spot_id"] for r in conn.execute(
        "SELECT DISTINCT spot_id FROM metric_snapshots WHERE spot_id IN ({})".format(
            ",".join("?" * len(NAME_BY_ID))), list(NAME_BY_ID))}
    spots |= {r["spot_id"] for r in conn.execute(
        "SELECT DISTINCT spot_id FROM content_assets WHERE spot_id IN ({})".format(
            ",".join("?" * len(NAME_BY_ID))), list(NAME_BY_ID))}
    # 也从关系表收集源头景区
    for r in conn.execute("SELECT DISTINCT source_id FROM spot_relations"):
        spots.add(r["source_id"])

    for sid in sorted(spots):
        if sid not in NAME_BY_ID:
            print(f"  ⚠️ 跳过未知 spot_id: {sid}")
            continue
        props = {
            "name": NAME_BY_ID[sid],
            "category": CATEGORY.get(sid, "未知"),
            "aliases": [sid],
            "tier": TIER.get(sid, "unknown"),
        }
        emit(sid, "ScenicSpot", props)

    # 1b. Region（rg_* 区位节点，located_in 的目标）
    print("=== M3 迁移: Region ===")
    region_names = {"rg_中牟": "中牟", "rg_开封": "开封", "rg_郑州": "郑州"}
    for rid, rname in region_names.items():
        props = {"name": rname, "level": "county" if "中牟" in rname else "city"}
        emit(rid, "Region", props)

    # 2. 关系（competes_with / located_in）
    print("=== M3 迁移: relations ===")
    for r in conn.execute("SELECT * FROM spot_relations"):
        src, tgt, rel = r["source_id"], r["target_id"], r["relation_type"]
        emit_rel(src, rel, tgt)
        rels.append(f"{src}-{rel}->{tgt}")

    # 3. MetricSnapshot（近期，避免全量爆炸：取每个景区最近 30 天）
    print("=== M3 迁移: MetricSnapshot（近30天）===")
    mcount = 0
    for r in conn.execute(
        "SELECT * FROM metric_snapshots WHERE spot_id IN ({}) "
        "AND date >= date('now','-30 day')".format(",".join("?" * len(NAME_BY_ID))),
        list(NAME_BY_ID)):
        eid = f"metric_{r['spot_id']}_{r['date']}_{r['metric_type']}"
        props = {
            "spot_id": r["spot_id"], "source": r["source"] or "douyin",
            "date": r["date"], "metric_type": r["metric_type"],
            "value": r["value"], "confidence": r["confidence"],
        }
        if r["daily_change"] is not None:
            props["daily_change"] = r["daily_change"]
        if r["weekly_change"] is not None:
            props["weekly_change"] = r["weekly_change"]
        emit(eid, "MetricSnapshot", props)
        if eid in created and r["spot_id"]:
            emit_rel(r["spot_id"], "has_metric", eid)

    # 4. TouristSegment（5 类）
    print("=== M3 迁移: TouristSegment ===")
    for r in conn.execute("SELECT * FROM tourist_segments"):
        eid = f"seg_{r['id']}" if not r["id"].startswith("seg_") else r["id"]
        props = {"name": r["name"]}
        for k in ("age_range", "region", "characteristics"):
            if r[k]:
                props[k] = r[k]
        if r["gender_split"]:
            props["gender_split"] = json.loads(r["gender_split"])
        emit(eid, "TouristSegment", props)

    # 5. ContentAsset
    print("=== M3 迁移: ContentAsset ===")
    ccount = 0
    for r in conn.execute(
        "SELECT * FROM content_assets WHERE spot_id IN ({})".format(
            ",".join("?" * len(NAME_BY_ID))), list(NAME_BY_ID)):
        eid = r["id"] or f"content_{r['external_id']}"
        props = {"source": r["source"] or "xiaohongshu", "title": r["title"] or "untitled"}
        if r["spot_id"]:
            props["spot_id"] = r["spot_id"]
        if r["url"]:
            props["url"] = r["url"]
        for k in ("author", "like_count", "comment_count", "share_count", "publish_date"):
            if r[k] is not None:
                props[k] = r[k]
        emit(eid, "ContentAsset", props)
        if eid in created and r["spot_id"]:
            emit_rel(eid, "published_by", r["spot_id"])

    conn.close()
    print(f"\n✅ M3 迁移完成: 新建实体 {len(created)}，跳过已存在 {skipped}，relations {len(rels)}")
    if args.dry_run:
        print("（DRY-RUN，未写入）")
    # 校验
    if not args.dry_run:
        import subprocess
        r = subprocess.run([sys.executable, str(WORKSPACE / "skills/ontology/scripts/ontology.py"),
                            "validate", "-g", str(GRAPH_PATH), "-s", str(SCHEMA_PATH)],
                           capture_output=True, text=True)
        print("validate:", r.stdout.strip() or r.stderr.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
