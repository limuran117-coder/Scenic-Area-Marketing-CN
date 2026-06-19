#!/opt/homebrew/bin/python3.12
"""
Ontology Adapter: 抖音指数 → MetricSnapshot Object

功能：
1. 读取 /tmp/crawl_data.json（douyin_index.py 输出）
2. 转换为 Ontology MetricSnapshot 对象
3. 写入 wiki/技术配置/Ontology架构设计/data/ 目录

数据格式对照（ontology.json → douyin_index.py）：
  MetricSnapshot.scenicSpotId ← spot.name（映射到 ScenicSpot id）
  MetricSnapshot.date         ← crawl_data.date
  MetricSnapshot.source       ← "douyin"
  MetricSnapshot.metricType   ← "search_index" | "composite_index"
  MetricSnapshot.value        ← spot.search | spot.synth
  MetricSnapshot.dailyChange  ← spot.search_trend | spot.synth_trend
  MetricSnapshot.collectedAt  ← crawl_data.crawled_at

运行：
  python3 adapter-douyin.py [--input /tmp/crawl_data.json] [--output data/]
"""

import json
import os
import sys
import datetime
import argparse
from pathlib import Path

# ─── 共享常量（来自 ontology_constants.py）─────

from ontology_constants import SCENIC_SPOT_MAP, resolve_spot_id, get_confidence

# D-020: confidence 统一从 ontology_constants.get_confidence('douyin') 取，不再硬编码 0.9

METRIC_TYPES = {
    "search": "search_index",
    "synth": "composite_index"
}

# ─── Ontology 对象构建 ──────────────────────────

def build_metric_object(scenic_spot_id, date_str, metric_type, value, daily_change, collected_at):
    """构建 MetricSnapshot Ontology 对象"""
    return {
        "schema": "MetricSnapshot",
        "version": "1.0.0",
        "id": f"{scenic_spot_id}::{date_str}::{metric_type}",
        "scenicSpotId": scenic_spot_id,
        "date": date_str,
        "source": "douyin",
        "metricType": metric_type,
        "value": value,
        "dailyChange": daily_change,
        "confidence": get_confidence("douyin"),
        "collectedAt": collected_at,
        "createdAt": datetime.datetime.now().isoformat()
    }

def parse_trend_to_number(trend_str):
    """将 '+2.5%' 转换为 2.5，'-1.3%' 转换为 -1.3"""
    if not trend_str:
        return 0.0
    cleaned = trend_str.replace('%', '').replace('+', '')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def transform_douyin_to_ontology(crawl_data):
    """将 douyin_index.py 输出转换为 MetricSnapshot 对象列表"""
    date_str = crawl_data.get("date", "")
    collected_at = crawl_data.get("crawled_at", "")
    competitors = crawl_data.get("competitors", [])
    
    ontology_objects = []
    transform_log = []
    
    for spot in competitors:
        name = spot.get("name", "")
        scenic_id = resolve_spot_id(name)
        
        # 搜索指数
        if spot.get("search", 0) > 0:
            obj = build_metric_object(
                scenic_spot_id=scenic_id,
                date_str=date_str,
                metric_type="search_index",
                value=spot["search"],
                daily_change=parse_trend_to_number(spot.get("search_trend", "")),
                collected_at=collected_at
            )
            ontology_objects.append(obj)
            transform_log.append(f"  [MetricSnapshot] {name} search_index = {spot['search']} ({spot.get('search_trend','')})")
        
        # 综合指数
        if spot.get("synth", 0) > 0:
            obj = build_metric_object(
                scenic_spot_id=scenic_id,
                date_str=date_str,
                metric_type="composite_index",
                value=spot["synth"],
                daily_change=parse_trend_to_number(spot.get("synth_trend", "")),
                collected_at=collected_at
            )
            ontology_objects.append(obj)
            transform_log.append(f"  [MetricSnapshot] {name} composite_index = {spot['synth']} ({spot.get('synth_trend','')})")
        
        # 异动标记（作为附加属性）
        if spot.get("anomaly", False):
            transform_log.append(f"  [⚠️ ANOMALY] {name} 有异动标记")
    
    return ontology_objects, transform_log

# ─── SQLite 双轨写入 ─────────────────────────────

def write_to_sqlite(objects, adapter_name="adapter-douyin"):
    """
    🔗 双轨策略: 将 MetricSnapshot 对象写入 SQLite
    返回: (inserted_count, error_message)
    """
    try:
        from ontology_store import OntologyStore
        store = OntologyStore()
        with store:
            count = store.ingest_metric_snapshots(objects, adapter_name)
        return count, None
    except Exception as e:
        return 0, str(e)[:200]


# ─── 输出 ────────────────────────────────────────

def write_ontology_output(objects, output_dir, date_str):
    """写入 ontology 格式数据到文件"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 按日期分文件存储
    date_compact = date_str.replace("-", "")
    file_path = output_path / f"metric_snapshots_{date_compact}.json"
    
    # 合并：如果有旧数据，保留旧数据避免覆盖（追加模式？不，覆盖当天数据）
    payload = {
        "objectType": "MetricSnapshot",
        "date": date_str,
        "generatedAt": datetime.datetime.now().isoformat(),
        "sourceAdapter": "adapter-douyin.py",
        "ontologyVersion": "1.0.0",
        "objects": objects,
        "count": len(objects)
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    return file_path


def write_daily_summary(objects, log_lines, output_dir, date_str):
    """写入工作日志"""
    log_path = Path(output_dir) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "date": date_str,
        "adapter": "adapter-douyin.py",
        "transformedCount": len(objects),
        "sourceFile": "/tmp/crawl_data.json",
        "status": "success" if objects else "no_data",
        "log": log_lines
    }
    
    log_file = log_path / f"adapter-douyin-{date_str.replace('-', '')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
    
    return log_file


# ─── 主逻辑 ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ontology Adapter: 抖音指数 → MetricSnapshot")
    parser.add_argument("--input", default="/tmp/crawl_data.json", help="douyin_index.py 输出路径")
    parser.add_argument("--output", default=None, help="ontology 数据输出目录")
    args = parser.parse_args()
    
    # 确定输出目录（默认：wiki/Ontology架构设计/data/）
    script_dir = Path(__file__).parent.resolve()
    output_dir = args.output or str(script_dir / "../wiki/技术配置/Ontology架构设计/data")
    output_dir = os.path.normpath(output_dir)
    
    # 读取输入
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"[❌] 输入文件不存在: {input_path}")
        print(f"[💡] 先运行 douyin_index.py 生成数据")
        return 1
    
    with open(input_path, 'r', encoding='utf-8') as f:
        crawl_data = json.load(f)
    
    date_str = crawl_data.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    print(f"\n{'='*60}")
    print(f"  Ontology Adapter: 抖音 → MetricSnapshot")
    print(f"  日期: {date_str}")
    print(f"{'='*60}")
    
    # 转换
    objects, log_lines = transform_douyin_to_ontology(crawl_data)
    
    if not objects:
        print(f"[⚠️] 没有有效数据可以转换")
        print(f"[📋] 转换日志:")
        for line in log_lines:
            print(line)
        return 0
    
    # 输出
    file_path = write_ontology_output(objects, output_dir, date_str)
    log_file = write_daily_summary(objects, log_lines, output_dir, date_str)
    
    print(f"\n[📋] 转换日志:")
    for line in log_lines:
        print(line)
    
    print(f"\n[✅] 成功转换 {len(objects)} 个 MetricSnapshot 对象")
    print(f"[📁] JSON输出: {file_path}")
    print(f"[📋] 日志: {log_file}")
    
    # 统计
    scenic_count = len(set(o["scenicSpotId"] for o in objects))
    types = set(o["metricType"] for o in objects)
    print(f"[📊] 覆盖景区: {scenic_count} 个")
    print(f"[📊] 度量类型: {', '.join(sorted(types))}")
    
    # 🔗 双轨: 同步写入 SQLite
    sqlite_count, sqlite_err = write_to_sqlite(objects, "adapter-douyin")
    if sqlite_err:
        print(f"[⚠️] SQLite 写入失败: {sqlite_err}")
        print(f"[💡] JSON 备份仍然有效，可稍后手动导入")
    else:
        print(f"[🗄️] SQLite: {sqlite_count} 条已写入 ontology_store.db")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
