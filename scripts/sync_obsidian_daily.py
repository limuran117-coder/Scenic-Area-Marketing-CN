#!/usr/bin/env python3
"""
每天自动同步数据到Obsidian Wiki
- 优先读取本地CSV最新数据（2026游客量统计.csv）
- 备用：飞书多维表格
- 更新当日日志文件
- 追加到历史分析文档
"""
import json
import subprocess
import csv
from datetime import datetime, timedelta

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

MEMORY_DIR = '/Users/tianjinzhan/.openclaw/workspace/memory'
OBSIDIAN_DIR = '/Users/tianjinzhan/.openclaw/workspace/wiki'
CSV_PATH = '/Users/tianjinzhan/Desktop/2026游客量统计.csv'

def read_csv_data():
    """从本地CSV读取最近数据"""
    try:
        with open(CSV_PATH, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # 返回最新的几条记录
        return rows[-5:] if len(rows) >= 5 else rows
    except Exception as e:
        print(f'CSV读取失败: {e}')
        return []

def get_feishu_data():
    """从飞书Bitable读取昨日数据（备用）"""
    FEISHU_APP = 'GmqWbb21zamf6pszdxncIVwkn4e'
    FEISHU_TABLE = 'tblQGnQGVI8THM3O'
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', '{"app_id":"cli_a941d5340639dcef","app_secret":"yNMaSBoHmrn9FcsrpWCzlcerQCD5aHji"}'
    ], capture_output=True, text=True, timeout=10)
    data = json.loads(result.stdout)
    token = data.get('tenant_access_token', '')
    if not token:
        return None
    
    yesterday_start = int(datetime.strptime(yesterday, '%Y-%m-%d').timestamp() * 1000)
    yesterday_end = int((datetime.strptime(yesterday, '%Y-%m-%d') + timedelta(days=1)).timestamp() * 1000)
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP}/tables/{FEISHU_TABLE}/records/search',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'filter': {'conjunction': 'and', 'conditions': [
                {'field_name': '日期', 'operator': 'between', 'value': [yesterday_start, yesterday_end]}
            ]}
        })
    ], capture_output=True, text=True, timeout=15)
    
    data = json.loads(result.stdout)
    items = data.get('data', {}).get('items', [])
    return items[0]['fields'] if items else None

def update_daily_log(rows):
    """更新memory日记文件"""
    log_path = f'{MEMORY_DIR}/{yesterday}.md'
    
    if not rows:
        print(f'{yesterday} 无数据')
        return
    
    # 找昨天的数据
    yesterday_row = None
    for r in rows:
        if r.get('日期', '').startswith(yesterday):
            yesterday_row = r
            break
    
    if not yesterday_row:
        print(f'{yesterday} CSV中无记录')
        return
    
    total = yesterday_row.get('合计', 0)
    weather = yesterday_row.get('天气', '')
    
    content = f"""
## 当日客流数据（自动同步）
- 合计客流: {total}
- 天气: {weather}
- 数据来源: 2026游客量统计.csv

"""
    try:
        with open(log_path, 'a') as f:
            f.write(content)
        print(f'已更新日志: {log_path}')
    except:
        pass

def update_obsidian_data(rows):
    """更新Wiki 2026年数据文件"""
    data_path = f'{OBSIDIAN_DIR}/电影小镇/历史数据/2026年/数据.md'
    
    if not rows:
        print('无数据可更新')
        return
    
    # 读取现有内容
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        content = ""
    
    # 更新每个有数据的日期
    updated = []
    for r in rows:
        date = r.get('日期', '')
        total = r.get('合计', '0')
        weekday = r.get('星期', '')
        weather = r.get('天气', '')
        
        if not date or date.startswith('2026') or total == '0':
            continue
        
        # 检查这行是否已存在
        import re
        pattern = rf'\| {re.escape(date)} \|'
        if re.search(pattern, content):
            # 替换已有的行
            old_line_pattern = rf'\| {re.escape(date)} \| [^\|]+ \| [^\|]+ \| [^\|]+ \|'
            new_line = f'| {date} | {weekday} | {weather} | {total} |'
            content = re.sub(old_line_pattern, new_line, content)
            updated.append(date)
    
    if updated:
        # 更新最后更新时间
        content = content.replace(
            '*AI Agent自动同步 | 最后更新：*',
            f'*AI Agent自动同步 | 最后更新：{today}*'
        )
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'已更新Wiki数据: {", ".join(updated)}')
    else:
        print('无需更新Wiki数据')

def main():
    print(f'=== Wiki数据同步 {today} ===')
    
    # 优先从CSV读取
    rows = read_csv_data()
    if rows:
        print(f'从CSV读取到 {len(rows)} 条记录')
        update_daily_log(rows)
        update_obsidian_data(rows)
    else:
        print('CSV无数据，尝试飞书...')
        data = get_feishu_data()
        if data:
            update_daily_log([data])
            print(f'飞书数据同步完成: {yesterday}')
        else:
            print(f'飞书也无数据: {yesterday}')

if __name__ == '__main__':
    main()
