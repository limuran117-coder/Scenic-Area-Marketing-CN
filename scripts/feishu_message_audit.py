#!/opt/homebrew/bin/python3.12
"""
飞书发消息审计脚本
触发: cron 每天 23:55
功能: 拉取当日 AI 发的消息，识别异常卡片并记录/推送
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

APP_ID = "cli_a941d5340639dcef"
APP_SECRET = "yNMaSBoHmrn9FcsrpWCzlcerQCD5aHji"
API_BASE = "https://open.feishu.cn/open-apis"
CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"
USER_CHAT_ID = "ou_f308d672765ecf1be73a75eb5e5f0f48"
SENDER_ID = "cli_a941d5340639dcef"
TIMEZONE = timezone(timedelta(hours=8))

ABNORMAL_KEYWORDS = ["test", "TEST", "测试", "调试", "debug", "dry-run", "占位"]

def get_token():
    url = f"{API_BASE}/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})
    req = urllib.request.Request(url, data=payload.encode(),
                                headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    if data.get("code") != 0:
        raise Exception(f"获取token失败: {data}")
    return data["tenant_access_token"]

def fetch_messages(token, start_time, end_time, page_size=50):
    """拉取飞书群消息，支持分页"""
    url = (f"{API_BASE}/im/v1/messages"
           f"?container_id_type=chat"
           f"&container_id={CHAT_ID}"
           f"&start_time={start_time}"
           f"&end_time={end_time}"
           f"&sort_type=ByCreateTimeDesc"
           f"&page_size={page_size}")
    headers = {"Authorization": f"Bearer {token}"}
    messages = []
    page_token = None

    while True:
        req_url = url
        if page_token:
            req_url = f"{url}&page_token={page_token}"
        req = urllib.request.Request(req_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        if data.get("code") != 0:
            raise Exception(f"拉取消息失败: {data}")
        items = data.get("data", {}).get("items", [])
        messages.extend(items)
        has_more = data.get("data", {}).get("has_more", False)
        if not has_more:
            break
        page_token = data.get("data", {}).get("page_token")
        if not page_token:
            break
    return messages

def extract_card_info(msg):
    """从消息中提取卡片信息"""
    msg_type = msg.get("msg_type", "")
    body_content = msg.get("body", {}).get("content", "")
    create_time = int(msg.get("create_time", 0))
    ts = datetime.fromtimestamp(create_time / 1000, tz=timezone.utc).astimezone(TIMEZONE)
    create_time_str = ts.strftime("%Y-%m-%d %H:%M:%S")

    title = ""
    body_preview = ""
    elements_count = 0

    try:
        card = json.loads(body_content)
        header = card.get("header", {})
        title = header.get("title", {}).get("content", "")
        body = card.get("body", {})
        elements = body.get("elements", [])
        elements_count = len(elements)
        body_texts = []
        for el in elements:
            if el.get("tag") == "markdown":
                body_texts.append(el.get("content", ""))
            elif el.get("tag") == "div":
                for sub in el.get("elements", []):
                    if sub.get("tag") == "markdown":
                        body_texts.append(sub.get("content", ""))
        body_preview = " ".join(body_texts)[:200]
    except (json.JSONDecodeError, KeyError, TypeError):
        body_preview = body_content[:200]

    return {
        "message_id": msg.get("message_id", ""),
        "create_time": create_time_str,
        "msg_type": msg_type,
        "title": title,
        "preview": body_preview,
        "elements_count": elements_count
    }

def is_abnormal(info):
    """判断是否为异常卡片"""
    reasons = []

    title_lower = info["title"].lower()
    for kw in ABNORMAL_KEYWORDS:
        if kw.lower() in title_lower:
            reasons.append(f"title含{kw}")
            break

    preview_lower = info["preview"].lower()
    for kw in ["test", "测试"]:
        if kw in preview_lower:
            reasons.append(f"body含{kw}")
            break

    if info["msg_type"] == "interactive" and info["elements_count"] < 2:
        reasons.append("疑似空卡片(elements<2)")

    return reasons

def main():
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    today_ymd = datetime.now(TIMEZONE).strftime("%Y%m%d")

    # 计算 start_time / end_time (今日 00:00 / 23:55 Asia/Shanghai)
    today_start = datetime.now(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now(TIMEZONE).replace(hour=23, minute=55, second=0, microsecond=0)
    start_ts = int(today_start.timestamp())
    end_ts = int(today_end.timestamp())

    token = get_token()
    messages = fetch_messages(token, start_ts, end_ts)

    # 筛选 AI 系统消息
    ai_messages = []
    for msg in messages:
        sender = msg.get("sender", {})
        if sender.get("id") == SENDER_ID and sender.get("sender_type") == "app":
            ai_messages.append(msg)

    # 提取卡片信息
    card_infos = []
    for msg in ai_messages:
        info = extract_card_info(msg)
        card_infos.append(info)

    # 识别异常
    abnormal = []
    for info in card_infos:
        reasons = is_abnormal(info)
        if reasons:
            abnormal.append({
                "message_id": info["message_id"],
                "create_time": info["create_time"],
                "title": info["title"],
                "preview": info["preview"],
                "reason": ",".join(reasons)
            })

    # 检测1分钟内重复发送
    seen = {}
    for info in card_infos:
        minute_key = info["create_time"][:16]  # YYYY-MM-DD HH:MM
        if minute_key in seen:
            reasons = is_abnormal(info)
            reasons.append(f"1分钟内重复({seen[minute_key]['message_id'][:20]}...)")
            abnormal.append({
                "message_id": info["message_id"],
                "create_time": info["create_time"],
                "title": info["title"],
                "preview": info["preview"],
                "reason": ",".join(reasons)
            })
        else:
            seen[minute_key] = info

    # 去重
    abnormal_ids = set()
    unique_abnormal = []
    for a in abnormal:
        if a["message_id"] not in abnormal_ids:
            abnormal_ids.add(a["message_id"])
            unique_abnormal.append(a)

    # 写入日志
    import os
    log_dir = os.path.expanduser("~/.openclaw/workspace/log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = f"{log_dir}/feishu_audit_{today_ymd}.json"

    audit_record = {
        "audit_date": today,
        "total_ai_messages": len(card_infos),
        "abnormal_count": len(unique_abnormal),
        "abnormal": unique_abnormal
    }

    with open(log_file, "w") as f:
        json.dump(audit_record, f, ensure_ascii=False, indent=2)

    print(f"审计完成: {today} | AI消息={len(card_infos)} | 异常={len(unique_abnormal)}")

    # 异常时推送给站长
    if len(unique_abnormal) > 0:
        table_rows = "| 时间 | 标题 | 异常原因 |\n|---|---|---|"
        for a in unique_abnormal:
            title_disp = a["title"][:30] if a["title"] else "(无标题)"
            preview_disp = a["preview"][:50] if a["preview"] else ""
            reason_disp = a["reason"]
            table_rows += f"\n| {a['create_time']} | {title_disp} | {reason_disp} |"

        card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "⚠️ 飞书发消息审计 · 异常"}},
            "body": {
                "elements": [{
                    "tag": "markdown",
                    "content": f"**审计日期**: {today}\n**AI 消息总数**: {len(card_infos)}\n**异常数**: {len(unique_abnormal)}\n\n{table_rows}"
                }]
            }
        }

        card_str = json.dumps(card, ensure_ascii=False)
        send_script = os.path.expanduser("~/.openclaw/workspace/scripts/send_feishu_card.py")
        import subprocess
        result = subprocess.run(
            ["python3", send_script, USER_CHAT_ID, card_str],
            capture_output=True, text=True
        )
        print(f"推送结果: {result.stdout} {result.stderr}")

if __name__ == "__main__":
    main()
