#!/opt/homebrew/bin/python3.12
"""文旅情报日报 2026-06-18 发送"""
import json
import sys
from send_feishu_card import send_card

CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"

with open("/Users/tianjinzhan/.openclaw/workspace/scripts/card_20260618.json", "r", encoding="utf-8") as f:
    card = json.load(f)

result = send_card(CHAT_ID, card, skip_validation=True)
print(f"\n{'✅ 发送成功' if result else '❌ 发送失败'}")
sys.exit(0 if result else 1)
