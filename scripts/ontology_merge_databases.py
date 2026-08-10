#!/usr/bin/env python3
"""
Ontology 双库合并迁移脚本（P2a：打通线下闭环）
================================================
背景：系统存在两个 ontology_store.py → 两个库割裂：
  - 生产库(workspace/.profile/ontology/ontology_store.db) —— 新版store, M6图谱钩子, douyin写入
  - 本家库(~/.profile/ontology/ontology_store.db)       —— 旧版store, 无M6, visitors/小红书/seed写入
      含 340条csv客流(线下核心! 2026-01~06) + 48 douyin + 36 xiaohongshu

目标：把本家库的关键数据安全并入生产库，让线下客流/内容资产进入图谱闭环。
原则：FAIL-SAFE —— 只新增生产库缺失的记录，绝不覆盖生产库已有更新数据；先dry-run, 再apply。

用法：
  python3 scripts/ontology_merge_databases.py --dry-run     # 预览将导入的数据（默认）
  python3 scripts/ontology_merge_databases.py --apply       # 实际执行
  python3 scripts/ontology_merge_databases.py --stats       # 两库统计对比
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PROD_DB = str(WORKSPACE / ".profile/ontology/ontology_store.db")
HOME_DB = str(Path.home() / ".profile/ontology/ontology_store.db")

# 本家库 csv 客流数据的 id 前缀（visitors adapter 生成）
CSV_ID_PREFIX = "metric_point_"


def sqlite(db) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def stats():
    print("=" * 70)
    print("两库统计对比")
    print("=" * 70)
    for label, db in [("生产库(workspace)", PROD_DB), ("本家库(home)", HOME_DB)]:
        if not Path(db).exists():
            print(f"  {label}: {db} [不存在]")
            continue
        c = sqlite(db)
        print(f"\n  {label}: {db}")
        for t in ["scenic_spots", "metric_snapshots", "content_assets", "spot_relations", "events"]:
            try:
                n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                print(f"    {t}: {n}")
            except Exception:
                print(f"    {t}: [无表]")
        try:
            rows = c.execute(
                "SELECT source, COUNT(*), MIN(date), MAX(date) FROM metric_snapshots GROUP BY source"
            ).fetchall()
            print(f"    metric来源:")
            for r in rows:
                print(f"      {r['source']}: {r['COUNT(*)']} 条 ({r['MIN(date)']}~{r['MAX(date)']})")
        except Exception as e:
            print(f"    metric来源查询失败: {e}")
        c.close()


def resolve_column(db, table, alias):
    """兼容 metadata / metadata_json 列名差异，返回该表实际存在的列名"""
    c = sqlite(db)
    cols = [r["name"] for r in c.execute(f"PRAGMA table_info({table})")]
    c.close()
    if alias in cols:
        return alias
    if alias == "metadata" and "metadata_json" in cols:
        return "metadata_json"
    if alias == "metadata_json" and "metadata" in cols:
        return "metadata"
    return None


def rows_to_import():
    """分析本家库应导入生产库的记录。返回 dict of tuples 供 insert。"""
    pc = sqlite(PROD_DB)
    hc = sqlite(HOME_DB)

    report = {"scenic_spots": [], "metrics": [], "content_assets": [], "skipped": []}

    # 1. scenic_spots：导入本家库有而生产库缺的 spot（用 id 判断）
    prod_spot_ids = {r["id"] for r in pc.execute("SELECT id FROM scenic_spots")}
    for r in hc.execute("SELECT * FROM scenic_spots"):
        if r["id"] in prod_spot_ids:
            report["skipped"].append(("scenic_spot_exist", r["id"]))
            continue
        report["scenic_spots"].append(dict(r))

    # 2. metric_snapshots：导入本家库有而生产库缺的 (spot_id, source, date, metric_type) 组合
    #    —— 保证不覆盖生产库已更新的 douyin 数据
    prod_metrics = {
        (r["spot_id"], r["source"], r["date"], r["metric_type"])
        for r in pc.execute("SELECT spot_id,source,date,metric_type FROM metric_snapshots")
    }
    h_meta = resolve_column(HOME_DB, "metric_snapshots", "metadata")
    col_expr = h_meta or "NULL"
    for r in hc.execute(f"SELECT * , {col_expr} AS metadata FROM metric_snapshots"):
        key = (r["spot_id"], r["source"], r["date"], r["metric_type"])
        if key in prod_metrics:
            report["skipped"].append(("metric_exist", key))
            continue
        report["metrics"].append(dict(r))

    # 3. content_assets：按 (id) 判断，导入本家库缺的
    prod_ca = {r["id"] for r in pc.execute("SELECT id FROM content_assets")}
    ca_meta = resolve_column(HOME_DB, "content_assets", "metadata")
    # content_assets 无 metadata 大字段，直接全列
    for r in hc.execute("SELECT * FROM content_assets"):
        if r["id"] in prod_ca:
            report["skipped"].append(("content_asset_exist", r["id"]))
            continue
        report["content_assets"].append(dict(r))

    pc.close()
    hc.close()
    return report


def apply_merge(report):
    pc = sqlite(PROD_DB)
    added = {"scenic_spots": 0, "metrics": 0, "content_assets": 0}

    # scenic_spots
    for s in report["scenic_spots"]:
        pc.execute(
            """INSERT OR IGNORE INTO scenic_spots
               (id,name,short_name,category,city,province,tier,annual_capacity,
                is_core_competitor,competitors,tags,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (s.get("id"), s.get("name"), s.get("short_name"), s.get("category"),
             s.get("city"), s.get("province"), s.get("tier", "secondary"),
             s.get("annual_capacity"), 1 if s.get("is_core_competitor") else 0,
             json.dumps(s.get("competitors", []), ensure_ascii=False),
             json.dumps(s.get("tags", []), ensure_ascii=False)),
        )
        added["scenic_spots"] += 1
    pc.commit()

    # metric_snapshots（列名兼容：生产库用 metadata）
    meta_col = "metadata"
    for m in report["metrics"]:
        raw = m.get("raw_data")
        meta = m.get("metadata") if isinstance(m.get("metadata"), (dict, str)) else None
        pc.execute(
            f"""INSERT OR REPLACE INTO metric_snapshots
               (id,spot_id,source,date,metric_type,value,daily_change,weekly_change,
                confidence,raw_data,{meta_col},ingested_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (m.get("id"), m.get("spot_id"), m.get("source"), m.get("date"),
             m.get("metric_type"), m.get("value"), m.get("daily_change"),
             m.get("weekly_change"), m.get("confidence", 0.5),
             raw, meta),
        )
        added["metrics"] += 1
    pc.commit()

    # content_assets（映射到生产库新版 schema 列）
    for ca in report["content_assets"]:
        mentions = ca.get("mentions") or []
        spot_id = mentions[0] if mentions else ca.get("scenic_spot_id") or ca.get("scenicSpotId") or ca.get("spot_id")
        pc.execute(
            """INSERT OR IGNORE INTO content_assets
               (id,schema,source,external_id,spot_id,title,description,url,author,
                like_count,comment_count,share_count,publish_date,content_type,
                platform,sentiment,tags,is_viral,raw_data,ingested_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (ca.get("id"), "ContentAsset", ca.get("source") or ca.get("platform"),
             ca.get("external_id"), spot_id, ca.get("title"), ca.get("description"),
             ca.get("url"), ca.get("author") or ca.get("author_name"),
             ca.get("like_count") or ca.get("likes", 0),
             ca.get("comment_count") or ca.get("comments", 0),
             ca.get("share_count") or ca.get("shares", 0),
             ca.get("publish_date"), ca.get("content_type") or ca.get("type"),
             ca.get("platform") or ca.get("source"), ca.get("sentiment"),
             json.dumps(ca.get("tags", []), ensure_ascii=False),
             1 if ca.get("is_viral") else 0,
             json.dumps(ca, ensure_ascii=False)),
        )
        added["content_assets"] += 1
    pc.commit()
    pc.close()
    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际执行合并（默认仅预览）")
    ap.add_argument("--stats", action="store_true", help="仅输出两库统计")
    args = ap.parse_args()

    if args.stats:
        stats()
        return

    report = rows_to_import()
    print("=" * 70)
    print("双库合并分析（预览）")
    print("=" * 70)
    for k in ["scenic_spots", "metrics", "content_assets"]:
        print(f"\n  [待导入 {k}]: {len(report[k])} 条")
        if report[k] and k == "metrics":
            srcs = {}
            for m in report[k]:
                srcs[m["source"]] = srcs.get(m["source"], 0) + 1
            print(f"    按来源: {srcs}")
    print(f"\n  [跳过(生产库已存在)]: {len(report['skipped'])} 条")

    if not args.apply:
        print("\n  （dry-run，未写入。加 --apply 执行）")
        return

    added = apply_merge(report)
    print("\n" + "=" * 70)
    print("合并执行完成")
    print("=" * 70)
    for k, v in added.items():
        print(f"  +{k}: {v} 条")
    print("\n  （注意：执行后需手动跑图谱同步，或等下次 adapter 写入触发）")


if __name__ == "__main__":
    main()
