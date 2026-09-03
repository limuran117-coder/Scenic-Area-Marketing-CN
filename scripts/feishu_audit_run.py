#!/opt/homebrew/bin/python3.12
"""飞书发消息审计 - 每日拉取群消息识别 test/debug 异常卡片
用法: python3 feishu_audit_run.py
输出: 打印 JSON 结果（调用方负责写日志文件）
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/Users/tianjinzhan/.openclaw/workspace/scripts")
from send_feishu_card import APP_ID, APP_SECRET, API_BASE, get_token

CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"
APP_SENDER = "cli_a941d5340639dcef"
TZ = timezone(timedelta(hours=8))

def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def fetch_messages(start_sec, end_sec):
    token = get_token()
    msgs = []
    page_token = ""
    for _ in range(20):  # 最多20页
        url = (f"{API_BASE}/im/v1/messages?container_id_type=chat&container_id={CHAT_ID}"
               f"&start_time={start_sec}&end_time={end_sec}"
               f"&sort_type=ByCreateTimeDesc&page_size=50")
        if page_token:
            url += f"&page_token={page_token}"
        data = api_get(url, token)
        if data.get("code") != 0:
            raise Exception(f"API错误: {data}")
        items = data.get("data", {}).get("items", [])
        msgs.extend(items)
        if data.get("data", {}).get("has_more"):
            page_token = data["data"].get("page_token", "")
        else:
            break
    return msgs

def parse_content(msg):
    """返回 (title, preview)"""
    msg_type = msg.get("msg_type", "")
    raw = msg.get("body", {}).get("content", "")
    try:
        content = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        content = {}
    title = ""
    preview = ""
    if msg_type == "interactive":
        header = content.get("header", {}) or {}
        t = header.get("title", {}) or {}
        title = t.get("content", "") if isinstance(t, dict) else ""
        body = content.get("body", {}) or {}
        elements = body.get("elements", []) or []
        preview = json.dumps(elements, ensure_ascii=False)[:200] if elements else ""
    elif msg_type == "text":
        preview = (content.get("text", "") if isinstance(content, dict) else str(content))[:200]
    elif msg_type == "post":
        preview = raw[:200]
    else:
        preview = raw[:200]
    return title, preview

def is_abnormal(msg, title, preview, now_sec):
    reasons = []
    body_text = preview.lower()
    joined = (title + " " + preview).lower()
    for kw in ["test", "调试", "debug", "dry-run", "占位", "dry run"]:
        if kw in joined and not (kw == "test" and "测试结果" in (title + preview)):
            reasons.append(f"含{kw!r}字样")
            break
    # 中文 测试（排除"测试结果"类合规用语）
    if "测试" in (title + preview) and "测试结果" not in (title + preview) and "测试中" not in (title + preview):
        reasons.append("含'测试'字样")
    msg_type = msg.get("msg_type", "")
    if msg_type == "interactive":
        try:
            content = json.loads(msg.get("body", {}).get("content", ""))
            elements = (content.get("body", {}) or {}).get("elements", []) or []
            if len(elements) < 2:
                reasons.append("空卡片(elements<2)")
        except Exception:
            pass
    return reasons

def main():
    now = datetime.now(TZ)
    # 窗口: 昨晚 23:55 → 今日 23:55（end 超出现在则取现在）
    start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(minutes=5)
    end_dt = now.replace(hour=23, minute=55, second=0, microsecond=0)
    end_dt = min(end_dt, now)
    start_sec = int(start_dt.timestamp())
    end_sec = int(end_dt.timestamp())

    msgs = fetch_messages(start_sec, end_sec)
    ai_msgs = [m for m in msgs if m.get("sender", {}).get("id", "") == APP_SENDER]

    abnormal = []
    for m in ai_msgs:
        title, preview = parse_content(m)
        reasons = is_abnormal(m, title, preview, now.timestamp())
        if reasons:
            ct = datetime.fromtimestamp(int(m["create_time"]) / 1000, TZ).strftime("%Y-%m-%d %H:%M:%S")
            abnormal.append({
                "message_id": m.get("message_id", ""),
                "create_time": ct,
                "title": title[:100],
                "preview": preview,
                "reason": ";".join(reasons),
            })

    result = {
        "audit_date": now.strftime("%Y-%m-%d"),
        "total_ai_messages": len(ai_msgs),
        "abnormal_count": len(abnormal),
        "abnormal": abnormal,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
