#!/usr/bin/env python3
"""高效批量插入飞书记录 - 剩余97条"""
import json
import subprocess
import time
from datetime import datetime

APP_TOKEN = "GmqWbb21zamf6pszdxncIVwkn4e"
TABLE_ID = "tblQGnQGVI8THM3O"
API_BASE = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

with open('/tmp/visitor_data_2026.json') as f:
    all_data = json.load(f)

# 跳过前23条(已插入)，插入剩余的
records_to_insert = all_data[23:]
print(f"开始插入 {len(records_to_insert)} 条记录...")

success = 0
fail = 0
for i, r in enumerate(records_to_insert):
    ts = int(datetime.strptime(r['date'], '%Y-%m-%d').timestamp() * 1000)
    
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

    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', API_BASE,
         '-H', 'Content-Type: application/json',
         '-d', payload],
        capture_output=True, text=True, timeout=10
    )

    if '"code":0' in result.stdout or '"msg":"success"' in result.stdout:
        print(f"[{i+24}] ✅ {r['date']} 客流:{r['total']}")
        success += 1
    else:
        print(f"[{i+24}] ❌ {r['date']} - {result.stdout[:80]}")
        fail += 1

    time.sleep(0.2)

print(f"\n完成! 成功:{success} 失败:{fail}")
