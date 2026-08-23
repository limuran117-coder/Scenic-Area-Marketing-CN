#!/usr/bin/env python3
"""周末市场观察卡片 2026-08-23 - 发送到电影小镇群（周末版）"""
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
            "content": "📌 周末版 · 文旅市场观察 | 2026-08-23(周日)"
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
                    "本周关键节点：**「七夕情歌夜」8/26(周三)启幕一直持续到8/31**，近万朵玫瑰「玫瑰阶梯」打卡点已就位，白天清新晚上变「星光花径」；另1.4米以下儿童免票延至8/31，正值暑期+七夕双窗口，本周末是预热前夜，宜提前造势。\n\n"
                    "**🏘 清明上河园（竞品）**\n"
                    "**大动作上新**：将推实景互动「攻打汴梁城」——游客在「督战队」带领下参与攻城，8/21已完成排练，多个景区（万岁山等）纷纷入局同款「游客参与式」实景玩法，沉浸式互动成当下顶流方向，与我们夜游/沉浸强相关，需盯紧。\n\n"
                    "**🏮 银基动物王国（竞品）**\n"
                    "暑期亲子游持续供需两旺，郑州+开封5天4晚亲子团热度走高，乐园+度假模式继续分流家庭客群，暑期尾声仍属强劲对手。\n\n"
                    "---\n\n"
                    "**🇨🇳 全国热点（1个）**\n"
                    "「游客参与式实景互动」成今夏现象级玩法：清明上河园攻城门、北京景山公园中轴线沉浸式夜游《奇喵夜》（8/16周末双场、AR数字交互）接连出圈，景区NPC/沉浸式互动体系大火——方向与电影小镇民国夜游+NPC高度契合。\n\n"
                    "---\n\n"
                    "## 🎯 本周最值得1个动作\n"
                    "**抢占「七夕情歌夜 + 游客参与式互动」双热点，趁周三七夕开幕前提前引爆**——主推玫瑰阶梯夜场+沉浸式互动体验，把前两天的预热期做成增量。\n"
                    "✅ 执行时间：周一(8/24)上午出预热方案，周二(8/25)上线推文/短视频造势\n\n"
                    "## 💡 周一启动建议\n"
                    "1. 借「七夕情歌夜」节点，本周主推夜间+情侣/亲子场景，上线玫瑰阶梯打卡内容与七夕特别节目预告。\n"
                    "2. 对标清明上河园「攻打汴梁城」，评估我们是否加码游客可参与的沉浸式互动环节，蹭「实景互动」全国流量。\n\n"
                    "---\n"
                    "⏰ 生成时间：2026-08-23 06:02 Asia/Shanghai"
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
