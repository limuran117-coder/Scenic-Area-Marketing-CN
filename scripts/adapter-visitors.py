#!/opt/homebrew/bin/python3.12
"""
Ontology Adapter: 客流CSV → MetricSnapshot Objects

数据源: ~/Desktop/2026游客量统计.csv（每周二更新）
字段映射:
  - Row 5:  日期表头（门票, 日期, 1月1日, ...）
  - Row 13: 门票人数合计（主数据）
  - Row 14: 门票收入金额（辅助数据）
  - metric_type="visitors" → 门票人数合计
  - metric_type="revenue"  → 门票收入金额

运行:
  python3 adapter-visitors.py [--csv ~/Desktop/2026游客量统计.csv]
"""

from __future__ import annotations
import json
import os
import sys
import csv
import datetime
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ontology_store import OntologyStore
from ontology_constants import MONTH_MAP, safe_float as _safe_float, get_confidence

# ─── 常量 ────────────────────────────────────────

CSV_PATH = Path.home() / "Desktop" / "2026游客量统计.csv"
SPOT_ID = "movie_town"
SOURCE = "csv"

# ─── CSV 解析 ────────────────────────────────────


def parse_date_header(cell: str) -> str | None:
    """解析 '1月1日' → '2026-01-01'"""
    cell = cell.strip()
    for month_str, month_num in MONTH_MAP.items():
        if month_str in cell:
            day_part = cell.replace(month_str, "").replace("日", "")
            if day_part.isdigit():
                day = int(day_part)
                return f"2026-{month_num}-{day:02d}"
    return None


def read_visitor_csv(csv_path: str = None) -> list[dict]:
    """读取CSV, 返回 [MetricSnapshot-Ontology-object, ...]"""
    csv_path = csv_path or str(CSV_PATH)
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV 文件不存在: {csv_path}")
        return []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = list(csv.reader(f))

    if len(reader) < 14:
        print(f"[ERROR] CSV 行数不足 ({len(reader)}行)")
        return []

    # Row 5（0-indexed: 4）是日期表头
    date_header = reader[4]
    dates = [parse_date_header(c) for c in date_header[2:]]  # 跳过"门票, 日期"两列
    
    # Row 13（0-indexed: 12）= 门票人数合计
    visitor_row = reader[12]
    # Row 14（0-indexed: 13）= 门票收入金额
    revenue_row = reader[13] if len(reader) > 13 else []

    objects = []
    
    for i, date_str in enumerate(dates):
        if not date_str:
            continue

        # 门票人数合计
        visitor_raw = visitor_row[i + 2] if i + 2 < len(visitor_row) else ""
        visitor_val = _safe_float(visitor_raw)
        if visitor_val is not None and visitor_val > 0:
            objects.append(_build_metric("visitors", date_str, visitor_val))

        # 门票收入金额
        revenue_raw = revenue_row[i + 2] if i + 2 < len(revenue_row) else ""
        revenue_val = _safe_float(revenue_raw)
        if revenue_val is not None and revenue_val > 0:
            objects.append(_build_metric("revenue", date_str, revenue_val))

    valid_dates = [d for d in dates if d]
    print(f"[OK] CSV解析完成: {len(objects)} 条数据 (截止 {valid_dates[-1] if valid_dates else 'N/A'})")
    return objects


def _build_metric(metric_type: str, date_str: str, value: float) -> dict:
    """构建 MetricSnapshot ontology object"""
    import hashlib
    key = f"{SPOT_ID}|{SOURCE}|{date_str}|{metric_type}"
    obj_id = "ms_" + hashlib.md5(key.encode()).hexdigest()[:12]

    return {
        "schema": "MetricSnapshot",
        "id": obj_id,
        "scenicSpotId": SPOT_ID,
        "source": SOURCE,
        "date": date_str,
        "metricType": metric_type,
        "value": value,
        "dailyChange": None,
        "weeklyChange": None,
        "confidence": get_confidence("csv"),
        "metadata": {
            "adapter": "adapter-visitors.py",
            "source_file": "2026游客量统计.csv",
            "collected_at": datetime.datetime.now().isoformat(),
        }
    }


# ─── 写入 Ontology Store ────────────────────────


def write_to_store(objects: list[dict]) -> int:
    """写入Ontology Store，返回写入行数"""
    with OntologyStore() as store:
        count = store.ingest_metric_snapshots(objects, adapter_name="visitors")
    return count


# ─── 主入口 ──────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="客流CSV → Ontology Store")
    parser.add_argument("--csv", default=str(CSV_PATH), help="CSV 文件路径")
    args = parser.parse_args()

    objects = read_visitor_csv(args.csv)
    if not objects:
        print("[FAIL] 无有效数据")
        sys.exit(1)

    # 统计信息
    visitors = [o for o in objects if o["metricType"] == "visitors"]
    revenues = [o for o in objects if o["metricType"] == "revenue"]
    
    if visitors:
        vals = [v["value"] for v in visitors if v["value"]]
        print(f"  客流数据: {len(visitors)} 条, 范围 {min(vals):.0f}~{max(vals):.0f}")
    if revenues:
        vals = [v["value"] for v in revenues if v["value"]]
        print(f"  收入数据: {len(revenues)} 条")

    count = write_to_store(objects)
    print(f"[DONE] 写入 Ontology Store: {count} 条")


if __name__ == "__main__":
    main()
