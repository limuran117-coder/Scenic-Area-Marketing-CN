#!/usr/bin/env python3
"""周末市场观察卡片 - 发送到电影小镇群"""
import json
import os
import sys
import urllib.request

APP_ID = "cli_a941d5340639dcef"
APP_SECRET = os.environ.get("OPENCLAW_FEISHU_APP_SECRET", "")
CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"

CARD = {
    "schema": "2.0",
    "header": {
        "title": {
            "tag": "plain_text",
            "content": "📌 周末版 · 文旅市场观察 | 2026-08-16(周日)"
        },
        "template": "blue"
    },
    "body": {
        "elements": [
            {
                "tag": "markdown",
                "content": (
                    "## 📌 周末3大景区速览\n\n"
                    "**🎬 建业电影小镇（本景区）**\n"
                    "暑期主打「回到小时候」怀旧主题：竹编躺椅、冰镇西瓜、老冰棍、露天电影，90年代跨代际记忆铺满园区；差异化体验带动营收增长，暑期家庭客群持续走高。\n\n"
                    "**🏛 只有河南·戏剧幻城（竞品）**\n"
                    "日均客流稳定在1.5万人次水平，品质客群优先；但近期与电影小镇一同被建业打包出售给信宸资本（总价30亿，戏剧幻城25亿+电影小镇5亿），折价超10亿，股权变更后营销打法或调整，值得持续盯。\n\n"
                    "**🌊 清明上河园（竞品）**\n"
                    "延续夏季荷风主题，万亩荷塘+宋韵演艺人气高，但节假日分流压力大（清明3天14万人次、单日最高9万），暑期旺季排队体验承压，反而是我们「人少体验优」的差异化机会点。\n\n"
                    "---\n\n"
                    "**🇨🇳 全国热点（1个）**\n"
                    "河南多景区推出2026中/高考生暑期免票福利（6/10-8/31，伏羲山、青龙山等），「准考证免票」成暑期流量抓手——青春客群出游热情高，值得关注。\n\n"
                    "---\n\n"
                    "## 🎯 本周最值得1个动作\n"
                    "**蹭「毕业免票」流量，快速上线中高考生专属套餐**（学生票+换装+非遗体验组合），借助准考证话题在小红书/抖音做一轮「暑期青春向」内容营销。\n"
                    "✅ 执行时间：周一(8/17)上午 10:30 前完成物料，下午上线\n\n"
                    "## 💡 周一启动建议\n"
                    "1. 针对暑期家庭+学生客群，主推「回到小时候」怀旧体验小红书图文/短视频，强化跨代际打卡。\n"
                    "2. 盯只有河南股权变更后的营销动作，第一时间做差异化应对。\n\n"
                    "---\n"
                    "⏰ 生成时间：2026-08-16 06:05 Asia/Shanghai"
                )
            }
        ]
    }
}

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    if data.get("code") != 0:
        raise RuntimeError("token failed: %s" % data)
    return data["tenant_access_token"]

def send_card(token):
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    body = json.dumps({
        "receive_id": CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(CARD, ensure_ascii=False)
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    if data.get("code") != 0:
        raise RuntimeError("send failed: %s" % data)
    return data

if __name__ == "__main__":
    if not APP_SECRET:
        sys.exit("OPENCLAW_FEISHU_APP_SECRET not set")
    tok = get_tenant_token()
    resp = send_card(tok)
    print(json.dumps(resp, ensure_ascii=False, indent=2))
    print("SENT OK")
