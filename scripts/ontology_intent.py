#!/usr/bin/env python3
"""
Ontology M5: LLM 智能层 —— 自然语言 → 图谱查询 → 结构化结果。

把"XX的竞品有哪些"这类业务问句翻译成语义化查询，交给 M4 查询层执行，
返回可直接用于洞察的结构化数据。

当前实现：规则+关键词匹配翻译（不依赖外部 LLM API，避免被配额卡死）。
架构上预留 LLM 槽位：query_plan = llm_translate(question) 可替换。

用法：
  python3 scripts/ontology_intent.py "电影小镇的竞品有哪些"
  python3 scripts/ontology_intent.py "中牟区域有哪些景区"
  python3 scripts/ontology_intent.py "电影小镇的最新搜索指数"
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE / "scripts"))
from ontology_graph_query import query_relations, name_of, load  # noqa: E402

# 景区 ID 别名表（与 SCENIC_SPOT_MAP 对齐）
SPOT_ALIASES = {
    "movie_town": ["电影小镇", "郑州电影小镇", "建业电影小镇", "电影*大片*"],
    "only_henan": ["只有河南", "只有河南戏剧幻城", "戏剧幻城"],
    "qingming_riverside": ["清明上河园", "清园", "上河园"],
    "yinji": ["银基", "银基动物王国", "动物王国"],
    "wansui_mountain": ["万岁山", "万岁山武侠城", "武侠城"],
    "fangte": ["方特", "方特欢乐世界"],
    "haichang": ["海昌", "海洋公园", "海昌海洋公园"],
    "only_dream": ["只有红楼梦", "红楼梦戏剧幻城"],
    "大唐不夜城": ["大唐不夜城", "不夜城"],
}
REGION_ALIASES = {"rg_中牟": ["中牟"], "rg_开封": ["开封"], "rg_郑州": ["郑州"]}

# 意图模式
INTENT_PATTERNS = {
    "competes": re.compile(r"竞品|竞争|对手|对抗|对标"),
    "located": re.compile(r"区位|位置|位于|同区|邻居|在哪个区域|属于"),
    "metrics": re.compile(r"指标|指数|搜索指数|综合指数|客流量|热度|数据"),
    "all": re.compile(r"全景|所有关系|全部|概况|简介"),
    "segments": re.compile(r"客群|人群|目标客户|受众|年轻|亲子"),
}
# 区域列举意图（"中牟有哪些景区" → 反查 located_in 的 source）
REGION_LIST_PATTERN = re.compile(r"(?:哪些|什么|有那些|有哪些|有哪|都(?:有|是)|景区|景点).*")


def resolve_spot(text: str):
    """从问句里解析出景区 ID，多词命中取最长。"""
    best_id, best_len = None, 0
    for sid, aliases in SPOT_ALIASES.items():
        for a in aliases:
            # 处理通配
            if "*" in a:
                pat = a.replace("*", ".*")
                if re.search(pat, text) and len(pat) > best_len:
                    best_id, best_len = sid, len(pat)
            elif a in text and len(a) > best_len:
                best_id, best_len = sid, len(a)
    return best_id


def resolve_intent(text: str):
    # 区域列举优先：含区域名 + 问"哪些"→ 区域景区清单（反查 located_in source）
    if recognize_region(text) and REGION_LIST_PATTERN.search(text):
        return "region_list"
    for intent, pat in INTENT_PATTERNS.items():
        if pat.search(text):
            return intent
    return "all"


def recognize_region(text: str):
    for rid, aliases in REGION_ALIASES.items():
        for a in aliases:
            if a in text:
                return rid
    return None


def translate(question: str) -> dict:
    """自然语言 → 查询计划。预留 LLM 槽位：可替换为 llm_translate()。"""
    intent = resolve_intent(question)
    spot = resolve_spot(question)
    region = recognize_region(question)
    return {"intent": intent, "spot": spot, "region": region, "raw": question}


def execute(plan: dict) -> dict:
    entities, _ = load()
    out = {"intent": plan["intent"], "question": plan["raw"]}

    if plan["intent"] in ("located", "region_list") and plan["region"]:
        # 问"中牟有哪些景区" → 反向 located_in
        r = query_relations(plan["region"], "located_in", "incoming")
        spots = [{"id": x["target_id"], "name": name_of(entities, x["target_id"])}
                 for x in r if x["entity"]]
        out["result"] = {"region": plan["region"], "scenic_spots_in_region": spots}
        return out

    if not plan["spot"]:
        out["error"] = "未识别到景区，请用：电影小镇/只有河南/清明上河园 等名称"
        return out

    if plan["intent"] == "competes":
        r = query_relations(plan["spot"], "competes_with")
        out["result"] = {"spot": plan["spot"],
                         "competitors": [{"id": x["target_id"], "name": name_of(entities, x["target_id"])}
                                          for x in r if x["entity"]]}
    elif plan["intent"] == "located":
        r = query_relations(plan["spot"], "located_in", "outgoing")
        out["result"] = {"spot": plan["spot"],
                         "located_in": [{"id": x["target_id"], "name": name_of(entities, x["target_id"])}
                                        for x in r if x["entity"]]}
    elif plan["intent"] == "metrics":
        r = query_relations(plan["spot"], "has_metric", "outgoing")
        latest = {}
        for x in r:
            e = x["entity"]
            if not e:
                continue
            p = e["properties"]
            mt = p.get("metric_type", "?")
            if mt not in latest or p.get("date", "") > latest[mt].get("date", ""):
                latest[mt] = {"date": p.get("date"), "value": p.get("value"),
                              "source": p.get("source"), "confidence": p.get("confidence")}
        out["result"] = {"spot": plan["spot"], "latest_metrics": latest}
    else:  # all 或未匹配
        r = query_relations(plan["spot"])
        rel_groups = {}
        for x in r:
            gt = x["relation"]
            rel_groups.setdefault(gt, []).append({
                "direction": x["direction"],
                "target": name_of(entities, x["target_id"]),
            })
        out["result"] = {"spot": plan["spot"], "name": name_of(entities, plan["spot"]),
                         "relation_groups": rel_groups}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="+", help="业务问句")
    ap.add_argument("--debug-plan", action="store_true", help="显示翻译出的查询计划")
    args = ap.parse_args()
    q = " ".join(args.question)
    plan = translate(q)
    if args.debug_plan:
        print(json.dumps({"plan": plan}, ensure_ascii=False, indent=2))
    result = execute(plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
