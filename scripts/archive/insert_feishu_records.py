#!/usr/bin/env python3
"""
批量插入飞书多维表格记录
"""
import json
import subprocess
import time
from datetime import datetime

APP_TOKEN = "GmqWbb21zamf6pszdxncIVwkn4e"
TABLE_ID = "tblQGnQGVI8THM3O"

def to_feishu_date(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return int(dt.timestamp() * 1000)

weekday_map = {
    'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
    'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
}

# 读取数据
with open('/tmp/visitor_data_2026.json', 'r') as f:
    data = json.load(f)

print(f"开始插入 {len(data)} 条记录...")

success = 0
failed = 0

for i, row in enumerate(data):
    record = {
        "fields": {
            "日期": to_feishu_date(row['date']),
            "星期": weekday_map.get(row['weekday'], row['weekday']),
            "天气备注": str(row['weather']) if row['weather'] else "",
            "门票-研学": row['yanxue'] if row['yanxue'] else 0,
            "门票-大客户期票": row['dakehu'] if row['dakehu'] else 0,
            "门票-导游司机": row['daoyou'] if row['daoyou'] else 0,
            "门票-旅行社团队": row['lvxing'] if row['lvxing'] else 0,
            "门票小计": row['menpiao'],
            "线上散客": row['xianshang'] if row['xianshang'] else 0,
            "合计客流": row['total'],
            "备注": ""
        }
    }
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records',
        '-H', 'Authorization: Bearer ' + open('/dev/stdin').read().strip() if False else 'Authorization: Bearer EMPTY',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(record, ensure_ascii=False)
    ], capture_output=True, text=True, timeout=10)
    
    if '"code":0' in result.stdout or '"msg":"success"' in result.stdout.lower():
        success += 1
    else:
        failed += 1
        print(f"  失败: {row['date']} - {result.stdout[:100]}")
    
    if (i + 1) % 10 == 0:
        print(f"进度: {i+1}/{len(data)} (成功:{success}, 失败:{failed})")
    
    time.sleep(0.1)  # 避免限流

print(f"\n完成! 成功:{success}, 失败:{failed}")
