#!/usr/bin/env python3
"""门票政策 CSV数据导入"""
import csv
import json
import subprocess
import time

APP_TOKEN = "IL0XbYQn8aeBcusrcYYcLhDZnDe"
TABLE_ID = "tbljx7DxgHJE0DPb"
API_BASE = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

rows = []
with open('/Users/tianjinzhan/Desktop/电影小镇_2026门票政策_飞书导入.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if row and row[0]:
            rows.append(row)

print(f"门票政策: {len(rows)} 条")

success = 0
for row in rows:
    try:
        fields = {
            "编号": int(row[0]) if row[0].isdigit() else 0,
            "政策名称": row[1] or '',
            "产品": row[2] or '',
            "售卖平台": row[3] or '',
            "售价": float(row[4]) if row[4] else 0,
            "结算价": row[5] or '',
            "售卖日期": row[6] or '',
            "使用有效期": row[7] or '',
            "库存数": int(row[8]) if row[8].isdigit() else 0,
            "限制": row[9] if len(row) > 9 else ''
        }
        payload = json.dumps({"fields": fields})
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', API_BASE,
             '-H', 'Content-Type: application/json', '-d', payload],
            capture_output=True, text=True, timeout=10
        )
        if '"code":0' in result.stdout:
            print(f"✅ {row[1][:20]}")
            success += 1
        else:
            print(f"❌ {row[0]}: {result.stdout[:60]}")
        time.sleep(0.2)
    except Exception as e:
        print(f"Error: {e}")

print(f"门票政策完成: {success}/{len(rows)}")
