#!/usr/bin/env python3
import json, subprocess, time, csv
from datetime import datetime

TOKEN = "t-g1044edFVZCJ3FSL7O734HL6ITS67STSPIK272ZC"
HDR = f"Authorization: Bearer {TOKEN}"

def date_ts(s):
    try:
        return int(datetime.strptime(s.strip(), '%Y/%m/%d').timestamp() * 1000)
    except:
        return None

APP = "QuWSbBx55aGF3Ksx8N2cW4Pln7c"
TBL = "tbltUc9G9bUjjrFr"
API = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP}/tables/{TBL}/records"

rows = []
with open('/Users/tianjinzhan/Desktop/电影小镇_价格排期_飞书导入.csv','r',encoding='utf-8-sig') as f:
    rdr = csv.reader(f)
    next(rdr)
    for row in rdr:
        if row and row[0]:
            rows.append(row)

print(f"价格排期: {len(rows)} 条", flush=True)
ok=fail=0
for row in rows:
    ts = date_ts(row[0])
    if not ts:
        print(f"SKIP: {row[0]}", flush=True)
        continue
    fields = {"日期":ts,"营业时间":row[1]or'',"门票价格":row[2]or'',"门票+剧场":row[3]or'',"加购":row[4]or'',"德化街场次":row[5]or''}
    res = subprocess.run(['curl','-s','-X','POST',API,'-H','Content-Type: application/json','-H',HDR,'-d',json.dumps({"fields":fields})], capture_output=True, text=True, timeout=10)
    if '"code":0' in res.stdout:
        ok+=1
    else:
        fail+=1
        print(f"ERR {row[0]}: {res.stdout[:80]}", flush=True)
    time.sleep(0.15)

print(f"完成: OK={ok} FAIL={fail}", flush=True)
