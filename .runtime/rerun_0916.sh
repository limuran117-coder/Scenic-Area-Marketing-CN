#!/bin/bash
IDS=(
  "a23a8099-59b2-4001-a63f-8b5bbf600484|抖音指数日报"
  "99dde0b3-ced3-457a-8f7c-2c2837687e50|竞品内容动态"
  "943c97b9-a900-411f-a757-679cf8e6ada7|每日复盘整合-内容生成"
  "0c6f51f7-1557-4f42-82a6-4f8075eae25d|cron自进化-每日哨兵"
  "b8fb57da-faae-429f-91e0-9f8af3db927b|竞品爆款拆解"
  "7ae9127b-40b1-4821-b82d-4e658e7295b9|飞书发消息审计"
  "553f1d57-61ba-4439-b4bf-eb725a36090c|文旅营销案例"
  "d3d91807-e0da-4b54-b000-d1caed42cff0|周二客流深度报告"
  "ea3cc4ec-8715-44ac-a843-bfa271424e2b|周度客流洞察"
  "cfb095fc-0c7c-4822-a470-e261f8c20555|Graphiti-Ontology同步"
)
LOG=/Users/tianjinzhan/.openclaw/workspace/.runtime/rerun_0916.log
: > "$LOG"
for entry in "${IDS[@]}"; do
  id="${entry%%|*}"; name="${entry##*|}"
  out=$(openclaw cron run "$id" 2>&1 | tr -d '\n' | head -c 160)
  echo "[$(date '+%H:%M:%S')] $name -> $out" >> "$LOG"
  sleep 75
done
echo "[$(date '+%H:%M:%S')] ALL DISPATCHED" >> "$LOG"
