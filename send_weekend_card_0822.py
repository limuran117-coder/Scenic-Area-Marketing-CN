#!/usr/bin/env python3
"""周末市场观察卡片 2026-08-22 - 发送到电影小镇群"""
import json
import os
import urllib.request

APP_ID = "cli_a941d5340639dcef"
APP_SECRET = os.environ.get("OPENCLAW_FEISHU_APP_SECRET", "")
CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"

CARD = {
    "schema": "2.0",
    "header": {
        "title": {
            "tag": "plain_text",
            "content": "📌 周末版 · 文旅市场观察 | 2026-08-22(周六)"
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
                    "暑期档收官冲刺：8月18日前后园区演艺密集、家庭客群进入暑期尾声小高潮，「周末游」+「夜场」是当下主力抓手，收尾期宜主打免排队/体验优的差异化。\n\n"
                    "**🏛 只有河南·戏剧幻城（竞品）**\n"
                    "全年客流超1800万、省外观众占比超八成，暑期依旧顶流需限流；但已同电影小镇一起被建业30亿出售给信宸资本（戏剧幻城25亿+电影小镇5亿），折价超10亿，股权变更后品牌与营销打法或调整，值得持续盯。\n\n"
                    "**🦁 银基动物王国（竞品）**\n"
                    "8月18日刚办4周年庆，上千名游客齐唱生日歌、暑期供需两旺营收持续增长；乐园+家庭度假模式对暑期家庭客群吸力强，是我们直接分流对手。\n\n"
                    "---\n\n"
                    "**🇨🇳 全国热点（1个）**\n"
                    "全国多省市暑期密集力推「周末游」（如广东『周末叹广东』、河北『这么近那么美』），周末短途周边游成今夏现象级流量抓手——「周末文化游」正在走红，方向与电影小镇周末+夜场契合。\n\n"
                    "---\n\n"
                    "## 🎯 本周最值得1个动作\n"
                    "**蹭「周末游」现象级热度 + 暑期收尾窗口，做强周末夜场/专场套餐**（如周六「周末特演场」+亲子套餐），锁定最后一批暑期家庭客，打差异化。\n"
                    "✅ 执行时间：周一(8/24)上午 10:30 前出方案，下午上线\n\n"
                    "## 💡 周一启动建议\n"
                    "1. 借「周末游」全国热点，主推电影小镇周末一日/夜游路线内容，强化「免排队·体验优」差异化。\n"
                    "2. 持续盯只有河南股权变更与银基周年庆后的营销动作，第一时间做应对。\n\n"
                    "---\n"
                    "⏰ 生成时间：2026-08-22 06:10 Asia/Shanghai"
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
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    body = json.dumps({
        "receive_id": CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(CARD, ensure_ascii=False)
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer " + token
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    if data.get("code") != 0:
        raise RuntimeError("send failed: %s" % data)
    return data

if __name__ == "__main__":
    token = get_tenant_token()
    res = send_card(token)
    print("OK", json.dumps(res, ensure_ascii=False)[:500])
