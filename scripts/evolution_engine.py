#!/usr/bin/env python3
"""
进化引擎（Evolution Engine）— 自我积累/验证/进化的数据层控制器
================================================================
背景（站长愿景 2026-08-10）：
  每天的搜索结果、任务产出、分析结论，必须沉淀成知识库固化积累，
  系统通过"产出→沉淀→验证→提炼→反馈"形成自我进化、越用越好。

本脚本是进化的【数据层】，负责：
  1. 盘点：统计结论索引三态、待验证结论清单、最新可用数据源
  2. 匹配：用最新数据（客流/抖音/图谱）匹配"待验证结论"候选，列出可验证项
  3. 矛盾：扫描已验证结论中的潜在矛盾（供 LLM 裁决）
  4. 输出：结构化 JSON，供 weekly 进化 cron 用 LLM 做最终判断推进

用法：
  python3 scripts/evolution_engine.py --inventory     # 结论库存盘点
  python3 scripts/evolution_engine.py --pending      # 待验证结论 + 可验证证据
  python3 scripts/evolution_engine.py --contradict   # 已验证结论矛盾扫描
  python3 scripts/evolution_engine.py --report       # 全量进化报告(默认)
"""
from __future__ import annotations
import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
CONCL = WORKSPACE / "wiki/行业知识/结论索引.md"
RULES = WORKSPACE / "wiki/行业知识/决策规则库.md"
VALID = WORKSPACE / "wiki/行业知识/验证记录.md"
PROD_DB = WORKSPACE / ".profile/ontology/ontology_store.db"


# ─── 结论索引解析 ────────────────────────────────
def parse_conclusions() -> dict:
    """解析结论索引 → {verified:[], pending:[], rejected:[]}"""
    if not CONCL.exists():
        return {"verified": [], "pending": [], "rejected": []}
    txt = CONCL.read_text(encoding="utf-8")
    # 按日期区块切分，识别每个表格的行
    result = {"verified": [], "pending": [], "rejected": []}
    # 每个表格行：以 | 开头，含 结论/置信度/来源/日期/状态
    for line in txt.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        concl, conf, source, d, status = cells[0], cells[1], cells[2], cells[3], "|".join(cells[4:])
        if not concl or concl.startswith("结论") or concl.startswith("---"):
            continue
        if len(concl) < 5:  # 跳过空/表头残留
            continue
        entry = {"text": concl, "conf": conf, "source": source, "date": d, "status": status}
        if "已验证" in status or "✅" in status:
            result["verified"].append(entry)
        elif "待验证" in status or "🔶" in status:
            result["pending"].append(entry)
        elif "推翻" in status or "修正" in status or "⚠️" in status:
            result["rejected"].append(entry)
        else:
            result["verified"].append(entry)  # 默认归为已验证
    return result


# ─── 最新数据盘点 ───────────────────────────────
def latest_data() -> dict:
    """从生产库盘点最新可验证数据"""
    out = {"db_exists": PROD_DB.exists()}
    if not PROD_DB.exists():
        return out
    c = sqlite3.connect(str(PROD_DB))
    try:
        # 各表最新日期
        for t, col in [("metric_snapshots", "date"), ("content_assets", "publish_date"),
                       ("tourist_segments", "ingested_at")]:
            try:
                row = c.execute(f"SELECT MAX({col}) FROM {t}").fetchone()
                out[f"{t}_latest"] = row[0] if row and row[0] else None
            except Exception:
                out[f"{t}_latest"] = None
        # 最近客流（csv visitors）
        try:
            rows = c.execute(
                """SELECT date, value FROM metric_snapshots
                   WHERE source='csv' AND metric_type='visitors'
                   ORDER BY date DESC LIMIT 7""").fetchall()
            out["recent_visitors"] = [{"date": r[0], "value": r[1]} for r in rows]
        except Exception:
            out["recent_visitors"] = []
        # 最近抖音搜索指数
        try:
            rows = c.execute(
                """SELECT date, value FROM metric_snapshots
                   WHERE source='douyin' AND metric_type='search_index'
                   ORDER BY date DESC LIMIT 7""").fetchall()
            out["recent_douyin"] = [{"date": r[0], "value": r[1]} for r in rows]
        except Exception:
            out["recent_douyin"] = []
    finally:
        c.close()
    return out


# ─── 待验证结论 × 证据匹配 ──────────────────────
def pending_with_evidence() -> list:
    """列出可尝试验证的待验证结论（供LLM据最新数据裁决）"""
    concl = parse_conclusions()
    data = latest_data()
    evidence = []
    for p in concl["pending"]:
        e = {"conclusion": p["text"], "conf": p["conf"], "source": p["source"],
             "date": p["date"], "status": p["status"], "evidence": []}
        t = p["text"]
        # 按关键词给证据提示
        if any(k in t for k in ["客流", "游客", "假日", "周末", "暑期"]):
            e["evidence"].append({"type": "visitors", "latest": data.get("recent_visitors", [])})
        if any(k in t for k in ["搜索指数", "抖音", "指数", "热度"]):
            e["evidence"].append({"type": "douyin", "latest": data.get("recent_douyin", [])})
        if any(k in t for k in ["竞品", "只有", "红楼梦", "河南", "方正"]):
            e["evidence"].append({"type": "graph", "note": "可用图谱查询竞品关系验证"})
        evidence.append(e)
    return evidence


# ─── 矛盾扫描 ──────────────────────────────────
def contradiction_scan() -> list:
    """在已验证结论中扫描潜在矛盾（同主题相反表述），供LLM裁决"""
    concl = parse_conclusions()
    verified = concl["verified"]
    # 简单启发式：找含数量级关键词的结论，标注主题，由 LLM 判断矛盾
    topics = {}
    for v in verified:
        t = v["text"]
        # 提取主题词
        theme = None
        for kw in ["客流", "搜索", "竞品", "只有河南", "只有红楼梦", "80年代",
                   "女性客群", "暑期", "端午", "静默", "资本"]:
            if kw in t:
                theme = kw
                break
        if theme:
            topics.setdefault(theme, []).append(v)
    # 输出同主题的结论组（潜在对比点）
    groups = []
    for theme, items in topics.items():
        if len(items) >= 2:
            groups.append({"theme": theme, "count": len(items),
                           "conclusions": [i["text"] for i in items[:3]]})
    return groups


# ─── 报告 ─────────────────────────────────────
def report():
    concl = parse_conclusions()
    data = latest_data()
    pend = pending_with_evidence()
    contra = contradiction_scan()
    out = {
        "generated_at": datetime.now().isoformat(),
        "inventory": {k: len(v) for k, v in concl.items()},
        "latest_data": data,
        "verifiable_pending": len(pend),
        "pending_evidence": pend[:15],
        "contradiction_themes": contra,
        "next_action": "由 weekly 进化 cron 用 LLM 依据 evidence 对每个待验证结论做 已验证/推翻 裁决，并写回结论索引",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def inventory():
    concl = parse_conclusions()
    print(f"结论索引三态: 已验证 {len(concl['verified'])} | 待验证 {len(concl['pending'])} | 已推翻/修正 {len(concl['rejected'])}")
    print(f"\n最近 8 条待验证:")
    for p in concl["pending"][-8:]:
        print(f"  [{p['date']}] {p['text'][:60]}...")


def pending():
    pend = pending_with_evidence()
    print(f"待验证结论 {len(pend)} 条，其中可用最新数据验证的候选：")
    n = 0
    for p in pend:
        if p["evidence"]:
            n += 1
            print(f"  ✅ [{p['date']}] {p['conclusion'][:55]}... 证据:{[e['type'] for e in p['evidence']]}")
    print(f"\n共 {n} 条可据最新数据裁决")


def contradict():
    contra = contradiction_scan()
    print(f"发现 {len(contra)} 个同主题结论组（潜在矛盾点，需LLM裁决）:")
    for g in contra:
        print(f"\n  [{g['theme']}] {g['count']}条结论:")
        for c in g["conclusions"]:
            print(f"    - {c[:50]}...")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--pending", action="store_true")
    ap.add_argument("--contradict", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    if args.inventory:
        inventory()
    elif args.pending:
        pending()
    elif args.contradict:
        contradict()
    else:
        report()


if __name__ == "__main__":
    main()
