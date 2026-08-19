#!/usr/bin/env python3
"""
客流周洞察同步到 Graphiti 时序知识图谱
用法:
  python sync_flow.py                # 同步最近 1 周洞察
  python sync_flow.py --weeks 4      # 同步最近 4 周洞察
  python sync_flow.py --all          # 同步 2026 全年周洞察

数据源: ~/Downloads/2026游客量统计 (N).csv (SSOT, 每周二更新)
目标:   FalkorDB graph 'movie-town' (Graphiti 时序图谱)

⚠️ 设计原则（8/19 踩坑总结）:
Graphiti 抽取的是"实体间关系"（RELATES_TO 边）。单实体数值（某天客流N人）
只产生 MENTIONS 边，检索不到。因此本脚本只写"关系型周洞察"：
  - 周客流峰值/均值 → 实体关系（如: 客流增长 → 由活动驱动）
  - 周环比趋势 → 关系事实
数值明细继续走 Excel/CSV 分析，Graphiti 只存关系洞察。
"""
import asyncio
import csv
import glob
import os
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graphiti_local import build_client

GROUP_ID = "movie-town"

def find_latest_csv():
    """找最新客流 CSV"""
    files = glob.glob(os.path.expanduser("~/Downloads/2026游客量统计*.csv"))
    if not files:
        raise FileNotFoundError("未找到客流 CSV！检查 ~/Downloads/2026游客量统计*.csv")
    return max(files, key=os.path.getmtime)

def parse_flow(csv_path):
    """解析门票人数合计行，返回 {天数索引: 客流数}（索引1=1月1日）"""
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip() == "门票人数合计":
                data = {}
                for i, val in enumerate(row[2:], start=1):
                    if val and val.strip():
                        try:
                            data[i] = int(float(val.strip()))
                        except ValueError:
                            pass
                return data
    raise ValueError("CSV 中未找到 门票人数合计 行")

def format_date(day_idx, year=2026):
    d = datetime(year, 1, 1) + timedelta(days=day_idx - 1)
    return d.strftime("%Y-%m-%d")

def build_weekly_insights(flow_data, weeks=1):
    """聚合每周客流 → 关系型洞察 episode"""
    valid_days = sorted([d for d, v in flow_data.items() if v > 0])
    if not valid_days:
        return []
    # 按 ISO 周分组
    week_groups = defaultdict(list)
    for day in valid_days:
        d = datetime(2026, 1, 1) + timedelta(days=day - 1)
        iso_year, iso_week, _ = d.isocalendar()
        week_groups[(iso_year, iso_week)].append((day, flow_data[day]))
    
    # 取最近 N 周（有数据的）
    sorted_weeks = sorted(week_groups.keys())
    recent_weeks = sorted_weeks[-weeks:]
    
    episodes = []
    for week_key in recent_weeks:
        days = week_groups[week_key]
        days_sorted = sorted(days)
        week_total = sum(v for _, v in days_sorted)
        week_avg = week_total / len(days_sorted)
        peak_day, peak_val = max(days_sorted, key=lambda x: x[1])
        peak_date = format_date(peak_day)
        
        # 对比上一周
        idx = sorted_weeks.index(week_key)
        trend_part = ""
        if idx > 0:
            prev_week = week_groups[sorted_weeks[idx - 1]]
            prev_total = sum(v for _, v in prev_week)
            if prev_total > 0:
                delta = (week_total - prev_total) / prev_total * 100
                direction = "增长" if delta >= 0 else "下降"
                trend_part = f"较上一周{direction}{abs(delta):.1f}%"
        
        # 关系型洞察（多实体）
        week_start = format_date(days_sorted[0][0])
        week_end = format_date(days_sorted[-1][0])
        body = (
            f"2026年第{week_key[1]}周（{week_start}至{week_end}），"
            f"郑州电影小镇周客流总量{week_total}人，日均{week_avg:.0f}人，{trend_part}。"
            f"周内客流峰值出现在{peak_date}，达{peak_val}人。"
            f"该周客流计入郑州电影小镇2026年度123万客流目标的完成进度。"
        )
        episodes.append({
            "name": f"客流周洞察-{week_key[0]}W{week_key[1]:02d}",
            "body": body,
            "date": week_start,
        })
    return episodes

async def sync(weeks=1):
    csv_path = find_latest_csv()
    print(f"📄 数据源: {csv_path}")
    flow_data = parse_flow(csv_path)
    print(f"📊 解析到 {len(flow_data)} 天有效客流数据")
    
    episodes = build_weekly_insights(flow_data, weeks)
    if not episodes:
        print("❌ 没有可同步的数据")
        return
    
    print(f"📝 准备写入 {len(episodes)} 条周洞察:")
    for ep in episodes:
        print(f"  - {ep['name']}: {ep['body'][:65]}...")
    
    g = build_client()
    for ep in episodes:
        ref_time = datetime.strptime(ep["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        await g.add_episode(
            name=ep["name"],
            episode_body=ep["body"],
            source_description="客流周洞察自动同步",
            reference_time=ref_time,
            group_id=GROUP_ID,
        )
        print(f"  ✅ 已写入: {ep['name']}")
    
    print(f"\n🎉 同步完成！共 {len(episodes)} 条周洞察")
    print("提示: 边构建需数秒，检索建议稍后执行")

if __name__ == "__main__":
    weeks = 1
    if "--all" in sys.argv:
        weeks = 9999
    elif "--weeks" in sys.argv:
        idx = sys.argv.index("--weeks")
        weeks = int(sys.argv[idx + 1])
    asyncio.run(sync(weeks))
