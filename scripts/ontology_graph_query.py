#!/usr/bin/env python3
"""
Ontology M4: 图谱关系查询层（Graph Query Layer）。

面向业务问题封装图谱引擎的关系查询，让"竞品是谁/区位在哪/谁的目标客群重叠"
这类关系型问题可以直接问，返回结构化结果供洞察使用。

用法：
  python3 scripts/ontology_graph_query.py competes movie_town
  python3 scripts/ontology_graph_query.py located movie_town
  python3 scripts/ontology_graph_query.py metrics movie_town --days 7
  python3 scripts/ontology_graph_query.py all movie_town   # 全景：一个景区所有关系
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE / "skills/ontology/scripts"))
import ontology as eng  # noqa: E402

GRAPH_PATH = Path(WORKSPACE) / "wiki/技术配置/Ontology架构设计/graph/graph.jsonl"


def load():
    return eng.load_graph(str(GRAPH_PATH))


def name_of(entities, eid: str) -> str:
    e = entities.get(eid, {})
    props = e.get("properties", {})
    return props.get("name") or eid


def query_relations(eid: str, rel_type: str | None = None, direction: str = "both"):
    """查询一个实体在某关系上的所有对象。返回 [{entity:{...}}] 结构（与引擎 related 一致）。"""
    entities, relations = load()
    results = []
    for rel in relations:
        if rel["from"] != eid and rel["to"] != eid:
            continue
        if rel_type and rel["rel"] != rel_type:
            continue
        is_out = rel["from"] == eid
        if direction == "outgoing" and not is_out:
            continue
        if direction == "incoming" and is_out:
            continue
        target = rel["to"] if is_out else rel["from"]
        results.append({
            "relation": rel["rel"],
            "direction": "outgoing" if is_out else "incoming",
            "entity": entities.get(target),
            "target_id": target,
        })
    return results


def cmd_competes(args):
    entities, _ = load()
    results = query_relations(args.id, "competes_with")
    competitors = [{"id": r["target_id"], "name": name_of(entities, r["target_id"])}
                   for r in results if r["entity"]]
    print(json.dumps({"spot": args.id, "competitors": competitors}, ensure_ascii=False, indent=2))


def cmd_located(args):
    entities, _ = load()
    results = query_relations(args.id, "located_in", "outgoing")
    locs = [{"id": r["target_id"], "name": name_of(entities, r["target_id"])}
            for r in results if r["entity"]]
    out = {"spot": args.id, "located_in": locs}
    # 反向：谁也在同一区位（兄弟景区）
    if locs:
        siblings = []
        for loc in locs:
            r2 = query_relations(loc["id"], "located_in", "incoming")
            for r in r2:
                if r["target_id"] != args.id and r["entity"]:
                    siblings.append({"id": r["target_id"], "name": name_of(entities, r["target_id"])})
        out["co_located_in_same_region"] = siblings
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_metrics(args):
    entities, _ = load()
    results = query_relations(args.id, "has_metric", "outgoing")
    # 按 metric 聚合最近值
    latest = {}
    by_metric = {}
    for r in results:
        e = r["entity"]
        if not e:
            continue
        props = e["properties"]
        mt = props.get("metric_type", "?")
        if mt not in by_metric or props.get("date", "") > by_metric[mt].get("date", ""):
            by_metric[mt] = {"date": props.get("date"), "value": props.get("value"),
                             "source": props.get("source"), "confidence": props.get("confidence")}
    print(json.dumps({"spot": args.id, "latest_metrics": by_metric}, ensure_ascii=False, indent=2))


def cmd_all(args):
    entities, _ = load()
    rel_groups = {}
    for r in query_relations(args.id):
        gt = r["relation"]
        rel_groups.setdefault(gt, []).append({
            "direction": r["direction"],
            "target": name_of(entities, r["target_id"]),
        })
    print(json.dumps({"spot": args.id, "name": name_of(entities, args.id),
                      "relation_groups": rel_groups}, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Ontology M4 关系查询层")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("competes", "located", "metrics", "all"):
        p = sub.add_parser(c)
        p.add_argument("id")
    args = ap.parse_args()
    {"competes": cmd_competes, "located": cmd_located,
     "metrics": cmd_metrics, "all": cmd_all}[args.cmd](args)


if __name__ == "__main__":
    main()
