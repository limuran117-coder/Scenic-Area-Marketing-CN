#!/bin/bash
# /tmp 临时文件清理 - 每日04:00运行
# 策略：保留今天，删除昨天及更早
# 包括：截图、marker文件、采集数据等

set -e

TODAY=$(date +%Y%m%d)
YESTERDAY=$(date -v-1d +%Y%m%d 2>/dev/null || date -d 'yesterday' +%Y%m%d)

echo "[$(date '+%H:%M:%S')] /tmp 清理开始 (今日=$TODAY, 昨日=$YESTERDAY)"

# 1. 删除 douyin_screenshot_*.png（除今天外）
# 策略：保留今日可能存在的截图，删除所有截图（明天起日报自己会重新生成）
DELETED=0
for f in /tmp/douyin_screenshot*.png /tmp/douyin_screenshot_*.png; do
  if [ -f "$f" ]; then
    rm -f "$f"
    DELETED=$((DELETED + 1))
  fi
done
echo "  截图清理: $DELETED 个"

# 2. 删除 marker 文件（除今天外）
# /tmp/.douyin_index_20260605 等
DELETED=0
for pattern in ".douyin_index_" ".daily_review_" ".weekly_competition_" ".weekly_memory_" ".system_evolution_" ".wiki_health_" ".ontology_daily_work_"; do
  for f in /tmp/${pattern}*; do
    if [ -f "$f" ]; then
      # 提取文件名中的日期
      fname=$(basename "$f")
      file_date=${fname#${pattern}}
      if [ "$file_date" != "$TODAY" ] && [ -n "$file_date" ]; then
        rm -f "$f"
        DELETED=$((DELETED + 1))
      fi
    fi
  done
done
echo "  Marker文件清理: $DELETED 个"

# 3. 删除 crawl_data.json（昨日的，保留今天的给日报读）
if [ -f /tmp/crawl_data.json ]; then
  # 看文件mtime
  file_age=$(( $(date +%s) - $(stat -f%m /tmp/crawl_data.json 2>/dev/null || stat -c%Y /tmp/crawl_data.json) ))
  if [ $file_age -gt 86400 ]; then
    rm -f /tmp/crawl_data.json
    echo "  crawl_data.json 清理: 1个 (${file_age}s前)"
  fi
fi

# 4. 删除 xhs_*.json 临时数据
DELETED=0
for f in /tmp/xhs_*.json /tmp/xiaohongshu_*.json; do
  if [ -f "$f" ]; then
    file_age=$(( $(date +%s) - $(stat -f%m "$f" 2>/dev/null || stat -c%Y "$f") ))
    if [ $file_age -gt 86400 ]; then
      rm -f "$f"
      DELETED=$((DELETED + 1))
    fi
  fi
done
echo "  XHS临时数据清理: $DELETED 个"

# 5. 删除 lock 文件（卡住的实例）
for f in /tmp/*.lock /tmp/*_lock; do
  if [ -f "$f" ]; then
    file_age=$(( $(date +%s) - $(stat -f%m "$f" 2>/dev/null || stat -c%Y "$f") ))
    if [ $file_age -gt 1800 ]; then  # 30分钟以上视为卡住
      rm -f "$f"
      echo "  卡住lock清理: $(basename $f) (${file_age}s前)"
    fi
  fi
done

# 6. 总结
TOTAL_SIZE=$(du -sh /tmp 2>/dev/null | cut -f1)
USED=$(df -h /tmp | tail -1 | awk '{print $5}')
echo "[$(date '+%H:%M:%S')] /tmp 清理完成 - 总占用 ${TOTAL_SIZE} (${USED} 满)"
