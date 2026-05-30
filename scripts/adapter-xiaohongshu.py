#!/opt/homebrew/bin/python3.12
"""
Ontology Adapter: 小红书数据 → MetricSnapshot + ContentAsset

功能：
1. 读取 /tmp/xiaohongshu_*.json（xiaohongshu_crawl.py 输出）
2. 双向映射到 Ontology：
   - MetricSnapshot: 内容总量（notes_count, engagement_index）
   - ContentAsset:  热门笔记详情（当爬虫升级支持时）
3. 写入 wiki/技术配置/Ontology架构设计/data/ 目录

数据格式对照（ontology.json → xiaohongshu_crawl.py）：
  MetricSnapshot.scenicSpotId ← keyword（映射到 ScenicSpot id）
  MetricSnapshot.date         ← crawled_at.date
  MetricSnapshot.source       ← "xiaohongshu"
  MetricSnapshot.metricType   ← "content_count" | "engagement_rate"
  MetricSnapshot.value        ← notes_count | avg_likes
  MetricSnapshot.confidence   ← 0.7（小红书数据置信度低于抖音索引）
  MetricSnapshot.collectedAt  ← crawled_at

  ContentAsset.id              ← f"xhs::{keyword}::{note_index}::date"
  ContentAsset.title           ← note title（预留）
  ContentAsset.platform        ← "xiaohongshu"
  ContentAsset.mentions        ← ScenicSpot.id（通过 keyword 映射）

设计原则（对标 Palantir OSDK）：
  - 每个数据源一个专用 adapter，生成类型安全的 Ontology 对象
  - 置信度记录：不同数据源置信度不同（抖音 0.9 > 小红书 0.7 > 百度 0.6）
  - 渐进式丰富：当前阶段先支持 MetricSnapshot，后续升级支持 ContentAsset

运行：
  python3 adapter-xiaohongshu.py [--input-dir /tmp/] [--keyword 建业电影小镇] [--output data/]
"""

import json
import os
import sys
import datetime
import argparse
import glob
from pathlib import Path

# ─── Ontology 常量 ──────────────────────────────

METRIC_TYPES = {
    "notes_count": "content_count",
    "avg_likes": "engagement_rate"
}

SCENIC_SPOT_MAP = {
    "建业电影小镇": "movie_town",
    "万岁山武侠城": "wansui_mountain",
    "清明上河园": "qingming_riverside",
    "只有河南": "only_henan",
    "只有河南戏剧幻城": "only_henan",
    "只有河南·戏剧幻城": "only_henan",
    "郑州方特欢乐世界": "fangte",
    "方特欢乐世界": "fangte",
    "郑州海昌海洋公园": "haichang",
    "郑州银基动物王国": "yinji",
    "银基动物王国": "yinji",
    "只有红楼梦戏剧幻城": "only_dream",
}

def parse_notes_count(notes_str):
    """解析 '约2.5万篇' → 25000"""
    if not notes_str or notes_str in ("—", "", "0"):
        return 0
    
    import re
    # 匹配 "约2.5万篇" 或 "1234篇笔记" 或 "1.2万"
    match = re.search(r'(\d+\.?\d*)\s*(万|千)?', str(notes_str))
    if not match:
        return 0
    
    num = float(match.group(1))
    unit = match.group(2)
    
    if unit == "万":
        num *= 10000
    elif unit == "千":
        num *= 1000
    
    return int(num)


def parse_likes_to_avg(likes_list):
    """解析点赞列表，计算平均点赞数"""
    if not likes_list:
        return 0
    
    total = 0
    count = 0
    for like_str in likes_list:
        import re
        match = re.search(r'(\d+\.?\d*)\s*(万|千)?', str(like_str))
        if match:
            num = float(match.group(1))
            unit = match.group(2)
            if unit == "万":
                num *= 10000
            elif unit == "千":
                num *= 1000
            total += num
            count += 1
    
    return int(total / count) if count > 0 else 0


# ─── Ontology 对象构建 ──────────────────────────

def build_metric_object(scenic_spot_id, date_str, metric_type, value, confidence, collected_at, metadata=None):
    """构建 MetricSnapshot Ontology 对象"""
    obj = {
        "schema": "MetricSnapshot",
        "version": "1.0.0",
        "id": f"{scenic_spot_id}::{date_str}::{metric_type}::xhs",
        "scenicSpotId": scenic_spot_id,
        "date": date_str,
        "source": "xiaohongshu",
        "metricType": metric_type,
        "value": value,
        "confidence": confidence,
        "collectedAt": collected_at,
        "createdAt": datetime.datetime.now().isoformat()
    }
    if metadata:
        obj["metadata"] = metadata
    return obj


def build_content_asset(scenic_spot_id, keyword, date_str, collected_at, note_index=0, note_data=None):
    """构建 ContentAsset Ontology 对象（预留，当爬虫升级后启用）"""
    obj = {
        "schema": "ContentAsset",
        "version": "1.0.0",
        "id": f"xhs::{keyword}::{date_str}::{note_index}",
        "title": note_data.get("title", f"{keyword}笔记#{note_index}") if note_data else f"{keyword}笔记#{note_index}",
        "platform": "xiaohongshu",
        "type": "note",
        "publishDate": date_str,
        "mentions": [scenic_spot_id],
        "collectedAt": collected_at,
        "createdAt": datetime.datetime.now().isoformat()
    }
    
    if note_data:
        obj["url"] = note_data.get("url", None)
        obj["authorName"] = note_data.get("author", None)
        obj["views"] = note_data.get("views", None)
        obj["likes"] = note_data.get("likes", None)
        obj["comments"] = note_data.get("comments", None)
        obj["tags"] = note_data.get("tags", [])
        # 根据互动数据判断是否爆款
        if note_data.get("likes", 0) > 1000:
            obj["isViral"] = True
    
    return obj


def transform_xiaohongshu_to_ontology(xhs_data):
    """将 xiaohongshu_crawl.py 输出转换为 Ontology 对象"""
    keyword = xhs_data.get("keyword", "")
    crawled_at = xhs_data.get("crawled_at", "")
    success = xhs_data.get("success", False)
    data = xhs_data.get("data", {})
    
    # 提取日期
    try:
        date_str = crawled_at[:10] if crawled_at else datetime.date.today().strftime("%Y-%m-%d")
    except:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 景区映射
    scenic_id = SCENIC_SPOT_MAP.get(keyword, keyword.lower().replace(" ", "_"))
    
    ontology_objects = []
    transform_log = []
    
    if not success:
        transform_log.append(f"  [⚠️] {keyword}: 采集失败，跳过")
        error_msg = xhs_data.get("error", "unknown")
        if "redirect_to_login" in str(error_msg):
            transform_log.append(f"      原因: 需要重新登录小红书")
        return ontology_objects, transform_log
    
    # ── MetricSnapshot: content_count ──
    notes_count = parse_notes_count(data.get("notes_approx", "0"))
    if notes_count > 0:
        obj = build_metric_object(
            scenic_spot_id=scenic_id,
            date_str=date_str,
            metric_type="content_count",
            value=notes_count,
            confidence=0.7,
            collected_at=crawled_at,
            metadata={"raw_notes_str": data.get("notes_approx", "")}
        )
        ontology_objects.append(obj)
        transform_log.append(f"  [MetricSnapshot] {keyword} content_count = {notes_count}")
    else:
        # 小红书爬虫暂无法提取精确笔记数，记录 content_length 作为替代
        content_length = data.get("content_length", 0)
        if content_length > 0:
            obj = build_metric_object(
                scenic_spot_id=scenic_id,
                date_str=date_str,
                metric_type="content_count",
                value=content_length,
                confidence=0.3,  # content_length 是估算值，置信度低
                collected_at=crawled_at,
                metadata={"estimation_method": "content_length_bytes", "raw_bytes": content_length}
            )
            ontology_objects.append(obj)
            transform_log.append(f"  [MetricSnapshot] {keyword} content_count ≈ {content_length}B (估算, confidence=0.3)")
        else:
            transform_log.append(f"  [⚠️] {keyword}: notes_count=0 且 content_length=0，生成占位记录")
            # 生成一个占位记录，方便后续追踪
            obj = build_metric_object(
                scenic_spot_id=scenic_id,
                date_str=date_str,
                metric_type="content_count",
                value=0,
                confidence=0.1,
                collected_at=crawled_at,
                metadata={"status": "no_data"}
            )
            ontology_objects.append(obj)
    
    # ── MetricSnapshot: engagement_rate (基于 top_likes) ──
    top_likes = data.get("top_likes", [])
    if top_likes:
        avg_likes = parse_likes_to_avg(top_likes)
        if avg_likes > 0:
            obj = build_metric_object(
                scenic_spot_id=scenic_id,
                date_str=date_str,
                metric_type="engagement_rate",
                value=avg_likes,
                confidence=0.6,  # 仅基于前5条笔记的估算
                collected_at=crawled_at,
                metadata={"sample_size": len(top_likes), "raw_top_likes": top_likes}
            )
            ontology_objects.append(obj)
            transform_log.append(f"  [MetricSnapshot] {keyword} engagement_rate = {avg_likes} (avg of top {len(top_likes)})")
    
    # ── ContentAsset: 热门笔记（预留）──
    # 当前 xiaohongshu_crawl.py 不输出详细笔记列表
    # 当爬虫升级后，在此处生成 ContentAsset 对象
    # for i, note in enumerate(data.get("notes", [])):
    #     obj = build_content_asset(scenic_id, keyword, date_str, crawled_at, i, note)
    #     ontology_objects.append(obj)
    
    return ontology_objects, transform_log


def transform_all_files(input_dir):
    """批量转换目录下所有 xiaohongshu_*.json 文件"""
    pattern = os.path.join(input_dir, "xiaohongshu_*.json")
    files = glob.glob(pattern)
    
    # 过滤 cookies 等非数据文件
    data_files = [f for f in files if "cookies" not in os.path.basename(f)]
    
    if not data_files:
        print(f"[⚠️] 未找到匹配的小红书数据文件: {pattern}")
        return [], []
    
    all_objects = []
    all_logs = []
    
    for file_path in sorted(data_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xhs_data = json.load(f)
            
            # 验证是否为 dict（排除数组格式的 cookies 文件）
            if not isinstance(xhs_data, dict):
                all_logs.append(f"  [⏭] 跳过非数据文件: {os.path.basename(file_path)}")
                continue
            
            objects, logs = transform_xiaohongshu_to_ontology(xhs_data)
            all_objects.extend(objects)
            all_logs.extend(logs)
        except Exception as e:
            all_logs.append(f"  [❌] 读取失败 {os.path.basename(file_path)}: {str(e)[:80]}")
    
    return all_objects, all_logs


# ─── 输出 ────────────────────────────────────────

def write_ontology_output(objects, output_dir, date_str):
    """写入 ontology 格式数据到文件"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    date_compact = date_str.replace("-", "")
    file_path = output_path / f"metric_snapshots_xhs_{date_compact}.json"
    
    # 按 objectType 分组
    metrics = [o for o in objects if o.get("schema") == "MetricSnapshot"]
    contents = [o for o in objects if o.get("schema") == "ContentAsset"]
    
    payload = {
        "objectType": "MetricSnapshot",
        "date": date_str,
        "generatedAt": datetime.datetime.now().isoformat(),
        "sourceAdapter": "adapter-xiaohongshu.py",
        "ontologyVersion": "1.0.0",
        "objects": objects,
        "summary": {
            "metricSnapshots": len(metrics),
            "contentAssets": len(contents),
            "scenicSpotsCovered": len(set(o["scenicSpotId"] for o in metrics)),
            "metricTypes": list(set(o["metricType"] for o in metrics))
        },
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
        "adapter": "adapter-xiaohongshu.py",
        "transformedCount": len(objects),
        "sourcePattern": "/tmp/xiaohongshu_*.json",
        "status": "success" if objects else "no_data",
        "log": log_lines
    }
    
    log_file = log_path / f"adapter-xiaohongshu-{date_str.replace('-', '')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
    
    return log_file


# ─── 主逻辑 ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ontology Adapter: 小红书 → MetricSnapshot + ContentAsset")
    parser.add_argument("--input-dir", default="/tmp", help="xiaohongshu_crawl.py 输出目录")
    parser.add_argument("--keyword", default=None, help="单关键词模式（指定时仅处理该文件）")
    parser.add_argument("--output", default=None, help="ontology 数据输出目录")
    args = parser.parse_args()
    
    # 确定输出目录
    script_dir = Path(__file__).parent.resolve()
    output_dir = args.output or str(script_dir / "../wiki/技术配置/Ontology架构设计/data")
    output_dir = os.path.normpath(output_dir)
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    print(f"\n{'='*60}")
    print(f"  Ontology Adapter: 小红书 → MetricSnapshot + ContentAsset")
    if args.keyword:
        print(f"  关键词: {args.keyword}")
    print(f"  日期: {today}")
    print(f"{'='*60}")
    
    # 读取输入
    if args.keyword:
        file_path = os.path.join(args.input_dir, f"xiaohongshu_{args.keyword}.json")
        if not os.path.exists(file_path):
            print(f"[❌] 文件不存在: {file_path}")
            return 1
        
        with open(file_path, 'r', encoding='utf-8') as f:
            xhs_data = json.load(f)
        
        objects, log_lines = transform_xiaohongshu_to_ontology(xhs_data)
        date_str = xhs_data.get("crawled_at", today)[:10]
    else:
        objects, log_lines = transform_all_files(args.input_dir)
        date_str = today
    
    if not objects:
        print(f"[⚠️] 没有有效数据可以转换")
        for line in log_lines:
            print(line)
        return 0
    
    # 输出
    file_path = write_ontology_output(objects, output_dir, date_str)
    log_file = write_daily_summary(objects, log_lines, output_dir, date_str)
    
    print(f"\n[📋] 转换日志:")
    for line in log_lines:
        print(line)
    
    # 统计
    metrics = [o for o in objects if o.get("schema") == "MetricSnapshot"]
    contents = [o for o in objects if o.get("schema") == "ContentAsset"]
    scenic_count = len(set(o["scenicSpotId"] for o in metrics))
    
    print(f"\n[✅] 成功转换 {len(objects)} 个 Ontology 对象")
    print(f"    MetricSnapshot: {len(metrics)} | ContentAsset: {len(contents)}")
    print(f"[📁] 输出: {file_path}")
    print(f"[📋] 日志: {log_file}")
    print(f"[📊] 覆盖景区: {scenic_count} 个")
    if metrics:
        types = set(o["metricType"] for o in metrics)
        print(f"[📊] 度量类型: {', '.join(sorted(types))}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
