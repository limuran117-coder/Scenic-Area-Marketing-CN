#!/usr/bin/env bash
# run_weekly_pattern_analysis.sh
# 每周一 09:00 运行 pattern_analysis.py，结果写入 wiki + 触发 P0 告警

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_DIR="$(dirname "$SCRIPT_DIR")"

# 分析最近2周（本周+上周对比）
OUTPUT_JSON="/tmp/weekly_pattern_analysis.json"

python3 "$SCRIPT_DIR/pattern_analysis.py" \
  --weeks 2 \
  --output-json "$OUTPUT_JSON" \
  2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "⚠️ pattern_analysis.py 失败，exit=$EXIT_CODE"
  exit 1
fi

# 读取 P0 告警，如果有则输出给飞书
P0_COUNT=$(python3 -c "
import json
try:
    with open('$OUTPUT_JSON') as f:
        data = json.load(f)
    all_p0 = [i for r in data.values() for i in r.get('p0_alerts', [])]
    print(len(all_p0))
except:
    print(0)
" 2>&1)

echo "分析完成，P0告警数: $P0_COUNT"

# 如果有 P0，生成告警摘要并打印供 cron 捕获
if [ "$P0_COUNT" -gt 0 ]; then
  echo "🔴 有 $P0_COUNT 个 P0 告警需要关注"
  python3 -c "
import json, datetime
with open('$OUTPUT_JSON') as f:
    data = json.load(f)
for k, r in sorted(data.items()):
    for p0 in r.get('p0_alerts', []):
        print(f'P0 [{p0.get(\"week\",\"?\")}]: {p0[\"title\"]}')
        print(f'  数据: {p0[\"data_fact\"]}')
        print(f'  建议: {p0[\"action\"]}')
        print()
"
fi

exit 0
