#!/usr/bin/env python3
"""退票登记 CSV数据导入"""
import csv
import json
import subprocess
import time

APP_TOKEN = "XfSxb878SaCMMGs7K6XcTNwanSb"
TABLE_ID = "tbl3HD9DK1TBZNHS"
API_BASE = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

rows = []
with open('/Users/tianjinzhan/Desktop/电影小镇_退票登记_飞书导入.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if row and row[0]:
            rows.append(row)

print(f"退票登记: {len(rows)} 条")

success = 0
for row in rows:
    try:
        fields = {
            "序号": int(row[0]) if row[0].isdigit() else 0,
            "渠道": row[1] or '',
            "票名": row[2] or '',
            "订单号": row[3] or '',
            "差异张数": int(row[4]) if row[4].isdigit() else 0,
            "差异金额": float(row[5]) if row[5] else 0,
            "退款日期": row[6] or '',
            "手机号": row[7] if len(row) > 7 else ''
        }
        payload = json.dumps({"fields": fields})
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', API_BASE,
             '-H', 'Content-Type: application/json', '-d', payload],
            capture_output=True, text=True, timeout=10
        )
        if '"code":0' in result.stdout:
            print(f"✅ {row[0]} {row[2][:15]}")
            success += 1
        else:
            print(f"❌ {row[0]}: {result.stdout[:60]}")
        time.sleep(0.2)
    except Exception as e:
        print(f"Error: {e}")

print(f"退票登记完成: {success}/{len(rows)}")
