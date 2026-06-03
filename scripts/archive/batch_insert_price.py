#!/usr/bin/env python3
"""价格排期 CSV数据导入"""
import csv
import subprocess
import time
from datetime import datetime, timedelta

APP_TOKEN = "QuWSbBx55aGF3Ksx8N2cW4Pln7c"
TABLE_ID = "tbltUc9G9bUjjrFr"
API_BASE = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

def excel_date(num):
    try:
        return int((datetime(1899, 12, 30) + timedelta(days=int(num))).timestamp() * 1000)
    except:
        return None

# 读取CSV
rows = []
with open('/Users/tianjinzhan/Desktop/电影小镇_价格排期_飞书导入.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if len(row) >= 6 and row[0]:
            rows.append(row)

print(f"价格排期: {len(rows)} 条")

success = 0
for row in rows:
    try:
        date_ts = excel_date(row[0].replace('/','-'))
        if not date_ts:
            continue
        fields = {
            "日期": date_ts,
            "营业时间": row[1] or '',
            "门票价格": row[2] or '',
            "门票+剧场": row[3] or '',
            "加购": row[4] or '',
            "德化街场次": row[5] or ''
        }
        payload = json.dumps({"fields": fields})
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', API_BASE,
             '-H', 'Content-Type: application/json', '-d', payload],
            capture_output=True, text=True, timeout=10
        )
        if '"code":0' in result.stdout:
            print(f"✅ {row[0]}")
            success += 1
        else:
            print(f"❌ {row[0]}: {result.stdout[:60]}")
        time.sleep(0.2)
    except Exception as e:
        print(f"Error: {e}")

print(f"价格排期完成: {success}/{len(rows)}")
