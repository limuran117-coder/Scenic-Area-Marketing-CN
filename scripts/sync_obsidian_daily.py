#!/opt/homebrew/bin/python3.12
"""
每天自动同步数据到 Obsidian Wiki（workspace版本 + Obsidian Vault）
- 从2026游客量统计.csv提取最新客流数据
- 同步到 ~/.openclaw/workspace/wiki 和 Obsidian Vault
- 同时同步当日memory日志 和 穿越德化街数据
"""
import csv
import os
import re
import shutil
from datetime import datetime, timedelta
from collections import defaultdict

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

MEMORY_DIR = '/Users/tianjinzhan/.openclaw/workspace/memory'
OBSIDIAN_DIR = '/Users/tianjinzhan/.openclaw/workspace/wiki'
OBSIDIAN_VAULT = '/Users/tianjinzhan/Downloads/Scenic-Area-Marketing-CN-main/wiki'
CSV_PATH = '/Users/tianjinzhan/Desktop/2026游客量统计.csv'

WD_CN = {0:'周一',1:'周二',2:'周三',3:'周四',4:'周五',5:'周六',6:'周日'}
BASE = datetime(2026, 1, 1)

def parse_csv():
    """解析2026游客量统计.csv，返回结构化数据"""
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        print(f'❌ CSV读取失败: {e}')
        return None, None, None
    
    # Row 3 = 天气, Row 12 = 门票人数合计, Row 14 = 闸机入园人次
    # Row 25 = 穿越德化街日期, Row 26=场次, Row 27=库存, Row 28=售卖
    weather = {}
    for i in range(2, len(rows[3])):
        v = rows[3][i].strip()
        if v: weather[BASE + timedelta(days=i-2)] = v
    
    tickets = {}
    for i in range(2, len(rows[12])):
        v = rows[12][i].strip()
        if v and v != '0': tickets[BASE + timedelta(days=i-2)] = int(v)
    
    chuanyue = {}
    for i in range(2, min(len(rows[25]), len(rows[28]))):
        label = rows[25][i].strip()
        if label:
            d = BASE + timedelta(days=i-2)
            chang = int(rows[26][i]) if rows[26][i].strip() else 0
            ku = int(rows[27][i]) if rows[27][i].strip() else 0
            sold = int(rows[28][i]) if rows[28][i].strip() else 0
            chuanyue[d] = (chang, ku, sold)
    
    return weather, tickets, chuanyue


def sync_memory_log(weather, tickets, chuanyue):
    """追加最新客流到当日的memory文件（找到最近可用日，写入今天而非那天）"""
    d = datetime.now() - timedelta(days=1)  # 昨日
    today_d = datetime.now()  # 今天 = memory 文件日期
    # 找不到昨日，找最近可用客流日
    if d not in tickets and tickets:
        fallback_d = max(tickets.keys())
        if fallback_d < datetime.now() - timedelta(days=2):
            print(f'  ⚠️ CSV数据太旧（截止{fallback_d.strftime("%Y-%m-%d")}），不写memory')
            return
        d = fallback_d
    if d not in tickets:
        print(f'  ⚠️ 无客流数据，跳过memory同步')
        return
    # 写今天的memory文件（不是fallback那天）
    log_path = f'{MEMORY_DIR}/{today_d.strftime("%Y-%m-%d")}.md'
    wt = weather.get(d, '')
    content = f"""
## 当日客流（自动同步 {today}）
- 数据日期: {d.strftime('%Y-%m-%d')} {WD_CN[d.weekday()]}（最近可用）
- 合计客流: {tickets[d]:,}
- 天气: {wt}
- 穿越德化街: {chuanyue.get(d, ('N/A','N/A','N/A'))[0]}场 / 观演{chuanyue.get(d, ('N/A','N/A','N/A'))[2]:,}人次

"""
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ 已追加memory: {os.path.basename(log_path)} (数据={d.strftime("%Y-%m-%d")})')
    except Exception as e:
        print(f'  ⚠️ memory 写入失败: {e}')


def sync_workspace_wiki(weather, tickets, chuanyue):
    """同步到workspace wiki（OBSIDIAN_DIR）"""
    # 更新时间戳
    last_date = max(tickets.keys()).strftime('%Y-%m-%d')
    data_path = f'{OBSIDIAN_DIR}/电影小镇/历史数据/2026年/数据.md'
    
    try:
        if not os.path.exists(data_path):
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            print(f'  ℹ️ 数据.md 不存在，跳过 workspace wiki 更新')
            return
        with open(data_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'最后更新：\d{4}-\d{2}-\d{2}', f'最后更新：{today}', content)
        content = re.sub(r'数据截止：[\d-]+', f'数据截止：{last_date}', content)
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ 已更新workspace wiki: 数据.md (截止{last_date})')
    except Exception as e:
        print(f'  ⚠️ workspace wiki 更新失败: {e}')


def sync_obsidian_vault():
    """同步workspace wiki → Obsidian Vault（同步关键文件）"""
    if not os.path.exists(OBSIDIAN_VAULT):
        print(f'⚠️ Obsidian Vault不存在: {OBSIDIAN_VAULT}')
        return
    
    # 增量同步的文件映射 (workspace → obsidian vault)
    mappings = [
        (f'{OBSIDIAN_DIR}/电影小镇/历史数据/2026年/数据.md',
         f'{OBSIDIAN_VAULT}/电影小镇/历史数据/2026年/数据.md'),
    ]
    for src, dst in mappings:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f'✅ 已同步到Obsidian Vault: {os.path.basename(dst)}')
        else:
            print(f'  ⚠️ 源文件不存在: {src}')


def main():
    print(f'=== Obsidian同步 {today} ===')
    
    weather, tickets, chuanyue = parse_csv()
    if tickets is None:
        print('❌ CSV解析失败，中止')
        return
    
    print(f'  客流数据: {len(tickets)}天, 截止{max(tickets.keys()).strftime("%Y-%m-%d")}')
    print(f'  穿越德化街: {len(chuanyue)}天演出数据')
    
    # 1. 同步到memory日志
    sync_memory_log(weather, tickets, chuanyue)
    
    # 2. 同步到workspace wiki
    sync_workspace_wiki(weather, tickets, chuanyue)
    
    # 3. 同步到Obsidian Vault
    sync_obsidian_vault()
    
    print('=== 同步完成 ===')

if __name__ == '__main__':
    main()
