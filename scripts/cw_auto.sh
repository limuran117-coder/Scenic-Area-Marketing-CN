#!/bin/bash
# CodeWhale 自动模式包装器 — 集成到电影小镇自动化系统
# 用法: cw_auto.sh "分析任务描述"
# 宪法VII Level 6(证据)源：Codewhale exec 输出作为实时证据输入到决策链

export PATH="$HOME/.npm-global/bin:$PATH"

if [ $# -eq 0 ]; then
    echo "用法: cw_auto.sh \"<分析任务描述>\""
    echo "示例: cw_auto.sh \"分析今天电影小镇抖音指数变化原因\""
    exit 1
fi

PROMPT="$1"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_FILE="/tmp/cw_output_${TIMESTAMP}.md"

echo "🐋 CodeWhale 自动分析中..."
echo "任务：${PROMPT}"
echo "---"

# 用 CodeWhale exec 自动模式执行
codewhale exec --auto --model deepseek-v4-flash "${PROMPT}" 2>&1 | tee "${OUTPUT_FILE}"

echo "---"
echo "✅ 输出已保存: ${OUTPUT_FILE}"
echo "分析完成时间：$(date '+%H:%M:%S')"
