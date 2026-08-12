#!/bin/bash
# cron_governor_daily.sh — 每日 cron 健康哨兵（纯脚本，零 LLM 开销）
# 用法: bash scripts/cron_governor_daily.sh
# 逻辑: 跑 governor --daily -> 若有异常任务 -> 发飞书简短提醒 + 写 memory；无异常则静默（只写状态）
set -e
WORKSPACE="$HOME/.openclaw/workspace"
PY="/Users/tianjinzhan/.local/bin/python3"
STATE="$WORKSPACE/scripts/.cron_governor"
LOG="$STATE/daily_$(date +%Y%m%d).txt"
mkdir -p "$STATE"

# 1. 生成当日报告（纯脚本，无 LLM）
cd "$WORKSPACE"
SD="$PY scripts/cron_governor.py --daily --days 1 2>&1"   # 近1天=昨日活跃窗口
"$PY" scripts/cron_governor.py --daily --days 14 > "$LOG" 2>&1 || true

# 2. 读 JSON 判断是否有异常任务
N_ISSUE=$("$PY" -c "
import json,os
p='$STATE/report_14d.json'
if not os.path.exists(p): print(0); raise SystemExit
r=json.load(open(p))
print(len(r.get('tasks',[])))
")
N_REC=$("$PY" -c "
import json,os
p='$STATE/report_14d.json'
if not os.path.exists(p): print(0); raise SystemExit
r=json.load(open(p))
print(len(r.get('recommendations',[])))
")
# 限流高峰（若多，说明当天模型状态差）
PEAK=$("$PY" -c "
import json,os
p='$STATE/report_14d.json'
if not os.path.exists(p): print(''); raise SystemExit
r=json.load(open(p))
print(','.join(f'{h}:00' for h in r.get('peak_hours',[])))
")

# 3. 静默采集，不发群（避免测试/刷屏误发生产群，发送交给每周治理由 LLM 决策）
#    结果写入 history.log 供人/LLM 查看，异常仅标记不打扰
if [ "${N_ISSUE:-0}" -gt "0" ]; then
  echo "[$(date '+%H:%M')] 异常任务${N_ISSUE}个、待优化${N_REC}项 → 已记录，待每周治理" >> "$LOG"
else
  echo "[$(date '+%H:%M')] 无异常，静默" >> "$LOG"
fi

# 4. 历史对比（连续2天异常升级？—— 简化，先记录）
echo "=== $(date '+%Y-%m-%d %H:%M') 哨兵完成: issues=${N_ISSUE} recs=${N_REC} peak=${PEAK} ===" >> "$STATE/history.log"
exit 0
