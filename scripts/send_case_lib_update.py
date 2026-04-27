import sys
import json
import subprocess

def send_card(chat_id, card):
    cmd = [
        "python3", "/Users/tianjinzhan/.openclaw/workspace/scripts/send_feishu_card.py",
        chat_id,
        json.dumps(card)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result

card = {
    "schema": "2.0",
    "header": {
        "title": {"tag": "plain_text", "content": "📚 案例库更新 | 2026-04-27（第18周）"},
        "template": "orange"
    },
    "body": {
        "elements": [
            {"tag": "markdown", "content": "## 📌 一、数据采集状态\n\n⚠️ 抖音/小红书/微博/B站均需登录认证，本期无法实时扫描公开内容\n\n**处理方式：** 基于近期竞品动态追踪，本期进行系统性复盘整理"},
            {"tag": "markdown", "content": "## 📌 二、库内优质案例推荐（W17-W18交叉期）\n\n🔥 **郑州海昌水下国潮**（04-24入库）\n• 视觉奇观 + 国潮文化融合，抖音综合指数涨幅 **+74.85%**（近30日涨幅第一）\n• 借鉴方向：稀缺性内容 × 低价套票引流\n\n🔥 **打铁花跨景区现象**（04-24入库）\n• 非遗文化 × 视觉奇观，多景区共同热推\n• 借鉴方向：电影小镇引入夜间视觉奇观表演\n\n🔥 **老君山短视频方法论**（04-20入库）\n• 传播链：美景本身 → 随手拍 → 社交分享 → 跟风打卡 → 持续裂变\n• 借鉴方向：打造\"随手拍就是民国大片\"的标志性打卡点\n\n🔥 **万岁山i人挑战**（04-16入库）\n• 人格标签（i人/e人）× 互动挑战，精准击中年青人群\n• 借鉴方向：设计\"戏精人格测试\"等电影小镇专属标签"},
            {"tag": "markdown", "content": "## 📌 三、案例库现状\n\n• 总案例数：**13个**（持续积累中）\n• 本期新增：0个（平台限制，无法实时扫描）\n• 覆盖维度：情景剧/互动挑战/POV视角/情绪张力/节日营销/夜游/打卡经济\n\n**下次扫描：** 2026-04-28 20:00"},
            {"tag": "markdown", "content": "---\n*数据来源：竞品动态追踪 + 行业观察 | 每周二/四/六更新*"}
        ]
    }
}

if __name__ == "__main__":
    chat_id = "oc_2581c03b79e4893cc3616b253d60f34e"
    send_card(chat_id, card)
