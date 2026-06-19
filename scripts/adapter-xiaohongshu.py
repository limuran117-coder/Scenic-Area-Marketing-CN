#!/opt/homebrew/bin/python3.12
"""
Ontology Adapter: 小红书搜索数据 → MetricSnapshot + ContentAsset

功能：
1. 读取 /tmp/xhs_daily_data.json（xhs_daily_collector.py 批量格式，优先）
   或 /tmp/xiaohongshu_*.json（xiaohongshu_crawl.py 单文件格式，回退）
2. 转换为 Ontology 对象（MetricSnapshot + ContentAsset 双向映射）
3. 写入 wiki/技术配置/Ontology架构设计/data/ 目录

支持两种数据格式：
  批量格式（xhs_daily_data.json）:
    results[].keyword, results[].success, results[].data.hit_count
  单文件格式（xiaohongshu_*.json）:
    keyword, success, data.notes_approx, data.top_likes

双向映射设计（对标 AgentO/Palantir OSDK）：
  - 正向：MetricSnapshot → 聚合自多个 ContentAsset (aggregated_from)
  - 反向：ContentAsset → 贡献给某个 MetricSnapshot (contributes_to)

运行：
  python3 scripts/adapter-xiaohongshu.py [--input-dir /tmp] [--output data/]
"""

import json
import os
import sys
import datetime
import argparse
import re
from pathlib import Path
from typing import Optional

# ─── 共享常量 ──────────────────────────────────

from ontology_constants import (
    SCENIC_SPOT_MAP,
    SCENIC_SPOT_REVERSE,
    CONFIDENCE_BY_SOURCE,
    resolve_spot_id,
)

# ─── 常量 ──────────────────────────────────────

XHS_CONFIDENCE = CONFIDENCE_BY_SOURCE.get("xiaohongshu", 0.3)
XHS_INPUT_PATTERN = "xiaohongshu_*.json"

# ─── 数据提取 ──────────────────────────────────

def parse_notes_count(notes_str: str) -> Optional[int]:
    """解析笔记数：'约3.2万篇' → 32000, '1250篇笔记' → 1250"""
    if not notes_str or notes_str == "—":
        return None
    # 万篇
    m = re.search(r'(\d+\.?\d*)万', notes_str)
    if m:
        return int(float(m.group(1)) * 10000)
    # 普通数字
    m = re.search(r'(\d+)', notes_str)
    if m:
        return int(m.group(1))
    return None

def parse_likes_count(likes_list: list) -> int:
    """估算总互动量"""
    if not likes_list:
        return 0
    total = 0
    for l in likes_list:
        m = re.search(r'(\d+\.?\d*)', str(l))
        if not m:
            continue
        v = float(m.group(1))
        if '万' in str(l):
            v *= 10000
        total += int(v)
    return total

# ─── Ontology 对象构建 ─────────────────────────

def build_content_asset(scenic_spot_id: str, date_str: str,
                        keyword: str, collected_at: str,
                        notes_count: int, likes_total: int) -> dict:
    """构建 ContentAsset Ontology 对象"""
    # 每个景区每天生成一个 ContentAsset 聚合（而非每条笔记一个）
    asset_id = f"xhs::{scenic_spot_id}::{date_str}::content_aggregate"
    return {
        "schema": "ContentAsset",
        "version": "1.0.0",
        "id": asset_id,
        "scenicSpotId": scenic_spot_id,
        "date": date_str,
        "type": "xiaohongshu_aggregate",
        "source": "xiaohongshu",
        "title": f"{keyword} - 小红书内容聚合 - {date_str}",
        "url": f"https://www.xiaohongshu.com/explore?channel_type=web_user_page&keyword={keyword}",
        "metrics": {
            "notes_count": notes_count,
            "likes_estimated": likes_total,
        },
        "collectedAt": collected_at,
        "confidence": XHS_CONFIDENCE,
        "createdAt": datetime.datetime.now().isoformat()
    }

def build_metric_snapshot(scenic_spot_id: str, date_str: str,
                          metric_type: str, value, collected_at: str,
                          content_asset_ids: list) -> dict:
    """构建 MetricSnapshot（关联到 ContentAsset）"""
    snap_id = f"{scenic_spot_id}::{date_str}::{metric_type}::xhs"
    return {
        "schema": "MetricSnapshot",
        "version": "1.0.0",
        "id": snap_id,
        "scenicSpotId": scenic_spot_id,
        "date": date_str,
        "source": "xiaohongshu",
        "metricType": metric_type,
        "value": value,
        "dailyChange": 0.0,  # 小红书暂不支持日环比较
        "confidence": XHS_CONFIDENCE,
        "collectedAt": collected_at,
        "metadata": {
            "content_asset_ids": content_asset_ids,
        },
        "createdAt": datetime.datetime.now().isoformat()
    }

# ─── 核心转换逻辑 ──────────────────────────────

def _process_one_result(result: dict) -> tuple:
    """处理单条小红书结果（来自批量或单文件格式）
    
    Returns: (content_asset, metric_snapshots, log_line)
             content_asset=None on error (check log_line for reason)
    """
    keyword = result.get("keyword", "")
    success = result.get("success", False)
    xhs_data = result.get("data", {}) or {}

    # 批量格式用 started_at，单文件格式用 crawled_at
    collected_at = result.get("crawled_at") or result.get("started_at", "")

    # 解析景区 ID
    scenic_id = resolve_spot_id(keyword)
    if not scenic_id:
        return None, [], f"  [⚠️] 未知关键词: {keyword}，跳过"

    if not success:
        err = result.get("error", "unknown")
        return None, [], f"  [❌] {keyword} 采集失败: {str(err)[:80]}"

    # hit_count → notes_count（批量格式专用字段）
    notes_count = xhs_data.get("hit_count")
    if notes_count is not None:
        notes_count = int(notes_count)
    else:
        # 单文件格式用 notes_approx
        notes_count = parse_notes_count(xhs_data.get("notes_approx", "—"))

    if notes_count is None:
        notes_count = 0

    # likes_total（批量格式暂无 top_likes）
    likes_total = parse_likes_count(xhs_data.get("top_likes", []))

    # 日期
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    if collected_at:
        try:
            dt = datetime.datetime.fromisoformat(collected_at)
            date_str = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass

    # ContentAsset
    content_asset = build_content_asset(
        scenic_spot_id=scenic_id,
        date_str=date_str,
        keyword=keyword,
        collected_at=collected_at,
        notes_count=notes_count,
        likes_total=likes_total,
    )
    content_asset["derivedToMetricSnapshot"] = f"{scenic_id}::{date_str}::content_count::xhs"

    asset_ids = [content_asset["id"]]

    # MetricSnapshot: content_count
    ms_content = build_metric_snapshot(
        scenic_spot_id=scenic_id,
        date_str=date_str,
        metric_type="content_count",
        value=notes_count,
        collected_at=collected_at,
        content_asset_ids=asset_ids,
    )

    # MetricSnapshot: engagement_rate
    # D-021: 当 likes_total=0 时，engagement_rate 缺失而非真实为 0
    # 标记 data_missing=true 让 query 层能区分"真零"与"数据缺失"
    has_likes_data = likes_total > 0 and notes_count > 0
    engagement = round(likes_total / notes_count, 1) if has_likes_data else 0.0
    ms_engage = build_metric_snapshot(
        scenic_spot_id=scenic_id,
        date_str=date_str,
        metric_type="engagement_rate",
        value=engagement,
        collected_at=collected_at,
        content_asset_ids=asset_ids,
    )
    if not has_likes_data:
        ms_engage["metadata"]["data_missing"] = True
        ms_engage["metadata"]["data_missing_reason"] = "xhs batch format lacks top_likes aggregate"

    log_line = f"  [✅] {keyword}: content_count={notes_count}, engagement_rate={engagement}, likes_est={likes_total}"
    return content_asset, [ms_content, ms_engage], log_line


def transform_xiaohongshu_to_ontology(input_dir: str):
    """读取所有小红书输出文件，转换为 Ontology 对象

    支持两种格式：
    1. 批量格式: /tmp/xhs_daily_data.json（xhs_daily_collector.py 输出）
    2. 单文件格式: /tmp/xiaohongshu_*.json（xiaohongshu_crawl.py 输出）
    """
    input_path = Path(input_dir)

    # ── 优先尝试批量格式（xhs_daily_collector.py）───
    batch_file = input_path / "xhs_daily_data.json"
    if batch_file.exists():
        all_content_assets = []
        all_metric_snapshots = []
        transform_log = []
        success_count = 0
        fail_count = 0

        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            transform_log.append(f"  [❌] 批量文件读取失败: {e}")
            return [], [], transform_log, datetime.date.today().strftime("%Y-%m-%d")

        results = batch_data.get("results", [])
        date_str = datetime.date.today().strftime("%Y-%m-%d")

        for result in results:
            content_asset, snapshots, log_line = _process_one_result(result)
            if content_asset is None:
                transform_log.append(log_line)
                fail_count += 1
            else:
                all_content_assets.append(content_asset)
                all_metric_snapshots.extend(snapshots)
                transform_log.append(log_line)
                success_count += 1

        transform_log.insert(0, f"批量格式 xhs_daily_data.json: {success_count} 成功, {fail_count} 失败")
        return all_content_assets, all_metric_snapshots, transform_log, date_str

    # ── 回退单文件格式 ────────────────────────────
    files = sorted(input_path.glob(XHS_INPUT_PATTERN))

    if not files:
        print("[⚠️] 未找到 /tmp/xiaohongshu_*.json 文件")
        print("[💡] 先运行 xhs_daily_collector.py 或 xiaohongshu_crawl.py 生成数据")
        return [], [], ""

    all_content_assets = []
    all_metric_snapshots = []
    transform_log = []
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    success_count = 0
    fail_count = 0

    for fpath in files:
        # 跳过非爬取输出文件（如 cookies.json）
        if "cookies" in fpath.name.lower():
            continue

        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            transform_log.append(f"  [❌] 读取失败: {fpath.name} — {e}")
            fail_count += 1
            continue

        # 跳过非字典格式
        if not isinstance(data, dict):
            transform_log.append(f"  [⏭️] 跳过非标准格式: {fpath.name} (type={type(data).__name__})")
            continue

        content_asset, snapshots, log_line = _process_one_result(data)
        if content_asset is None:
            transform_log.append(log_line)
            fail_count += 1
        else:
            all_content_assets.append(content_asset)
            all_metric_snapshots.extend(snapshots)
            transform_log.append(log_line)
            success_count += 1

    transform_log.insert(0, f"单文件格式: {success_count} 成功, {fail_count} 失败")
    return all_content_assets, all_metric_snapshots, transform_log, date_str


# ─── 输出 ──────────────────────────────────────

def write_ontology_output(objects, output_dir, date_str, object_type="MetricSnapshot"):
    """写入 ontology 格式数据到文件"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    date_compact = date_str.replace("-", "")
    prefix = "content_assets" if "ContentAsset" in object_type else "metric_snapshots"
    file_path = output_path / f"{prefix}_xhs_{date_compact}.json"

    payload = {
        "objectType": object_type,
        "date": date_str,
        "generatedAt": datetime.datetime.now().isoformat(),
        "sourceAdapter": "adapter-xiaohongshu.py",
        "ontologyVersion": "1.0.0",
        "objects": objects,
        "count": len(objects)
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return file_path


def write_daily_summary(all_objects, log_lines, output_dir, date_str):
    """写入工作日志"""
    log_path = Path(output_dir) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "date": date_str,
        "adapter": "adapter-xiaohongshu.py",
        "transformedCount": len(all_objects),
        "contentAssetCount": sum(1 for o in all_objects if o.get("schema") == "ContentAsset"),
        "metricSnapshotCount": sum(1 for o in all_objects if o.get("schema") == "MetricSnapshot"),
        "sourceDir": "/tmp/xhs_daily_data.json",
        "status": "success" if all_objects else "no_data",
        "log": log_lines
    }

    log_file = log_path / f"adapter-xiaohongshu-{date_str.replace('-', '')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)

    return log_file


# ─── SQLite 双轨写入 ─────────────────────────────

def write_to_sqlite(content_assets, metric_snapshots, adapter_name="adapter-xiaohongshu"):
    """双轨策略: 写 ContentAsset + MetricSnapshot 到 SQLite"""
    try:
        from ontology_store import OntologyStore
        store = OntologyStore()
        with store:
            ca_count = store.ingest_content_assets(content_assets, adapter_name)
            ms_count = store.ingest_metric_snapshots(metric_snapshots, adapter_name)
        return ca_count, ms_count, None
    except Exception as e:
        return 0, 0, str(e)[:200]


# ─── 主逻辑 ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ontology Adapter: 小红书 → ContentAsset + MetricSnapshot")
    parser.add_argument("--input-dir", default="/tmp", help="xiaohongshu_crawl.py 输出目录")
    parser.add_argument("--output", default=None, help="ontology 数据输出目录")
    args = parser.parse_args()

    # 确定输出目录
    script_dir = Path(__file__).parent.resolve()
    output_dir = args.output or str(script_dir / "../wiki/技术配置/Ontology架构设计/data")
    output_dir = os.path.normpath(output_dir)

    print(f"\n{'='*60}")
    print(f"  Ontology Adapter: 小红书 → ContentAsset + MetricSnapshot")
    print(f"  双向映射模式: aggregated_from ↔ contributes_to")
    print(f"{'='*60}")

    # 转换
    content_assets, metric_snapshots, log_lines, date_str = transform_xiaohongshu_to_ontology(args.input_dir)

    all_objects = content_assets + metric_snapshots

    if not all_objects:
        print(f"[⚠️] 没有有效数据可以转换")
        for line in log_lines:
            print(line)
        return 0

    # 输出
    ca_path = write_ontology_output(content_assets, output_dir, date_str, "ContentAsset")
    ms_path = write_ontology_output(metric_snapshots, output_dir, date_str, "MetricSnapshot")
    log_file = write_daily_summary(all_objects, log_lines, output_dir, date_str)

    print(f"\n[📋] 转换日志:")
    for line in log_lines:
        print(line)

    print(f"\n[💾] 写入文件:")
    print(f"  ContentAsset:   {ca_path} ({len(content_assets)} 个)")
    print(f"  MetricSnapshot: {ms_path} ({len(metric_snapshots)} 个)")
    print(f"  日志:           {log_file}")

    # SQLite 双轨写入
    ca_count, ms_count, err = write_to_sqlite(content_assets, metric_snapshots)
    if err:
        print(f"\n[⚠️] SQLite 写入失败: {err}")
    else:
        print(f"\n[✅] SQLite: ContentAsset ×{ca_count}, MetricSnapshot ×{ms_count}")

    return len(all_objects)


if __name__ == "__main__":
    sys.exit(main())