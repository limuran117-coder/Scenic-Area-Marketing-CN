#!/usr/bin/env python3
"""
批量插入飞书记录 - 直接调用API
"""
import json
import subprocess
import time

APP_TOKEN = "GmqWbb21zamf6pszdxncIVwkn4e"
TABLE_ID = "tblQGnQGVI8THM3O"

# 主表120天数据 (from visitor_data_2026.json)
visitor_data = [
    (1769360400000, "周一", "正常天", 0, 0, 0, 0, 0, 0, 0),  # 1/1 already done
    # ... (skip first 23)
]

# 完整的97条数据 (from index 23 to 120)
data_batch = [
    (1769184000000, "周六", "正常天", 0, 0, 2, 55, 57, 1259, 1316),
]

# Read from file and generate all remaining records
with open('/tmp/visitor_data_2026.json') as f:
    import json
    all_data = json.load(f)

print(f"Total records to insert: {len(all_data) - 23}")

# Insert records 24-120 (skip first 23 already inserted)
for i, r in enumerate(all_data[23:], start=24):
    ts = int(time.mktime(time.strptime(r['date'], '%Y-%m-%d')) * 1000
    fields = {
        "日期": ts,
        "星期": r['weekday'],
        "天气备注": r['weather'] or '',
        "门票-研学": r['yanxue'],
        "门票-大客户期票": r['dakehu'],
        "门票-导游司机": r['daoyou'],
        "门票-旅行社团队": r['lvxing'],
        "门票小计": r['menpiao'],
        "线上散客": r['xianshang'],
        "合计客流": r['total'],
        "备注": ""
    }
    
    payload = json.dumps({"fields": fields})
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records',
        '-H', 'Content-Type: application/json',
        '-d', payload
    ], capture_output=True, text=True, timeout=10)
    
    if '"code":0' in result.stdout:
        print(f"[{i}] OK: {r['date']} - {r['total']}")
    else:
        print(f"[{i}] FAIL: {r['date']} - {result.stdout[:100]}")
    
    time.sleep(0.15)  # avoid rate limit

print("Done!")
