#!/opt/homebrew/bin/python3.12
"""
Ontology Adapter: 小红书搜索数据 → MetricSnapshot + ContentAsset

功能：
1. 读取 /tmp/xiaohongshu_*.json（xiaohongshu_crawl.py 输出）
2. 转换为 Ontology 对象（MetricSnapshot + ContentAsset 双向映射）
3. 写入 wiki/技术配置/Ontology架构设计/data/ 目录

双向映射设计（对标 AgentO/Palantir OSDK）：
  - 正向：MetricSnapshot → 聚合自多个 ContentAsset (aggregated_from)
  - 反向：ContentAsset → 贡献给某个 MetricSnapshot (contributes_to)

数据格式对照（xiaohongshu_crawl.py → ontology.json）：
  ContentAsset.id          ← f"xhs::{spot_id}::{date}::note_{n}"
  ContentAsset.type        ← "xiaohongshu_note"
  ContentAsset.source      ← "xiaohongshu"
  ContentAsset.metrics.engagement ← top_likes 数量/估算

  MetricSnapshot.scenicSpotId ← SCENIC_SPOT_MAP[keyword]
  MetricSnapshot.metricType   ← "content_count" | "engagement_rate"
  MetricSnapshot.value        ← notes_approx | 估算互动率

运行：
  python3 scripts/adapter-xiaohongshu.py [--input-dir /tmp] [--output data/]

⚠️ 当前小红书爬虫 data 字段稀疏（仅 notes_approx + top_likes），
   待爬虫升级后（笔记详情/互动数/发布时间），ContentAsset 将更丰富。
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
        "url": f"https://www.xiaohongshu.com/search_result?keyword={keyword}",
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

def transform_xiaohongshu_to_ontology(input_dir: str):
    """读取所有小红书输出文件，转换为 Ontology 对象"""
    input_path = Path(input_dir)
    files = sorted(input_path.glob(XHS_INPUT_PATTERN))
    
    if not files:
        print("[⚠️] 未找到 /tmp/xiaohongshu_*.json 文件")
        print("[💡] 先运行 xiaohongshu_crawl.py 生成数据")
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
        
        keyword = data.get("keyword", "")
        success = data.get("success", False)
        collected_at = data.get("crawled_at", "")
        xhs_data = data.get("data", {})
        
        # 解析景区 ID
        scenic_id = resolve_spot_id(keyword)
        if not scenic_id:
            transform_log.append(f"  [⚠️] 未知关键词: {keyword}，跳过")
            continue
        
        if not success:
            err = data.get("error", "unknown")
            transform_log.append(f"  [❌] {keyword} 采集失败: {err[:80]}")
            fail_count += 1
            continue
        
        # 解析数据
        notes_count = parse_notes_count(xhs_data.get("notes_approx", "—"))
        likes_total = parse_likes_count(xhs_data.get("top_likes", []))
        
        if notes_count is None:
            transform_log.append(f"  [⚠️] {keyword} 笔记数为空，仅记录 ContentAsset")
            notes_count = 0
        
        # 更新日期（使用采集日期）
        try:
            dt = datetime.datetime.fromisoformat(collected_at)
            date_str = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
        
        # 构建 ContentAsset（双向映射：正向引用）
        content_asset = build_content_asset(
            scenic_spot_id=scenic_id,
            date_str=date_str,
            keyword=keyword,
            collected_at=collected_at,
            notes_count=notes_count,
            likes_total=likes_total,
        )
        # 反向引用：ContentAsset 知道自己贡献了哪个快照
        content_asset["derivedToMetricSnapshot"] = f"{scenic_id}::{date_str}::content_count::xhs"
        all_content_assets.append(content_asset)
        
        asset_ids = [content_asset["id"]]
        
        # 构建 MetricSnapshot: content_count
        ms_content = build_metric_snapshot(
            scenic_spot_id=scenic_id,
            date_str=date_str,
            metric_type="content_count",
            value=notes_count,
            collected_at=collected_at,
            content_asset_ids=asset_ids,
        )
        all_metric_snapshots.append(ms_content)
        
        # 构建 MetricSnapshot: engagement_rate（估算）
        if likes_total > 0 and notes_count > 0:
            engagement = round(likes_total / notes_count, 1)
        else:
            engagement = 0
        ms_engage = build_metric_snapshot(
            scenic_spot_id=scenic_id,
            date_str=date_str,
            metric_type="engagement_rate",
            value=engagement,
            collected_at=collected_at,
            content_asset_ids=asset_ids,
        )
        all_metric_snapshots.append(ms_engage)
        
        transform_log.append(
            f"  [✅] {keyword}: content_count={notes_count}, "
            f"engagement_rate={engagement}, likes_est={likes_total}"
        )
        success_count += 1
    
    transform_log.insert(0, f"共 {len(files)} 个文件: {success_count} 成功, {fail_count} 失败")
    
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
        "sourceDir": "/tmp/xiaohongshu_*.json",
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
    
    print(f"\n[✅] 成功转换 {len(content_assets)} 个 ContentAsset + {len(metric_snapshots)} 个 MetricSnapshot")
    print(f"[📁] ContentAsset: {ca_path}")
    print(f"[📁] MetricSnapshot: {ms_path}")
    print(f"[📋] 日志: {log_file}")
    
    # 统计
    scenic_ids = set(o["scenicSpotId"] for o in all_objects if "scenicSpotId" in o)
    metric_types = set(o["metricType"] for o in metric_snapshots if "metricType" in o)
    print(f"[📊] 覆盖景区: {len(scenic_ids)} 个")
    print(f"[📊] 度量类型: {', '.join(sorted(metric_types))}")
    
    # 🔗 双轨: 同步写入 SQLite
    ca_sqlite, ms_sqlite, sqlite_err = write_to_sqlite(content_assets, metric_snapshots, "adapter-xiaohongshu")
    if sqlite_err:
        print(f"[⚠️] SQLite 写入失败: {sqlite_err}")
        print(f"[💡] JSON 备份仍然有效，可稍后手动导入")
    else:
        print(f"[🗄️] SQLite: {ca_sqlite} ContentAsset + {ms_sqlite} MetricSnapshot 已写入")
    
    # 双向映射验证
    print(f"\n[🔗] 双向映射验证:")
    for ca in content_assets:
        derived_to = ca.get("derivedToMetricSnapshot", "MISSING")
        print(f"  ContentAsset::{ca['id'][:50]} → {derived_to}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
