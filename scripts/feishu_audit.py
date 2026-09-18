#!/opt/homebrew/bin/python3.12
"""飞书发消息审计：拉取当天群消息 → 筛选 AI 系统消息 → 识别异常卡片 → 写日志 → 异常时推送站长私聊"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_feishu_card import get_token, send_card  # 复用鉴权，不重写

API_BASE = "https://open.feishu.cn/open-apis"
CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"
BOT_APP_ID = "cli_a941d5340639dcef"
OWNER_OPEN_ID = "ou_f308d672765ecf1be73a75eb5e5f0f48"
LOG_DIR = os.path.expanduser("~/.openclaw/workspace/log")
CST = timezone(timedelta(hours=8))

BAD_WORDS = ["test", "测试", "调试", "debug", "dry-run", "占位"]
# 合规用法白名单（含这些则不算异常）
OK_WORDS = ["测试结果", "压力测试", "测试成功"]


def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def fetch_messages(token, start_ts, end_ts):
    msgs, page_token = [], None
    for _ in range(20):
        url = (f"{API_BASE}/im/v1/messages?container_id_type=chat&container_id={CHAT_ID}"
               f"&start_time={start_ts}&end_time={end_ts}&sort_type=ByCreateTimeDesc&page_size=50")
        if page_token:
            url += f"&page_token={page_token}"
        data = api_get(url, token)
        if data.get("code") != 0:
            raise Exception(f"拉取消息失败: {data}")
        d = data.get("data", {})
        msgs.extend(d.get("items", []))
        if not d.get("has_more"):
            break
        page_token = d.get("page_token")
    return msgs


def ts_to_str(ms):
    return datetime.fromtimestamp(int(ms) / 1000, CST).strftime("%Y-%m-%d %H:%M:%S")


def parse_card(body_raw):
    """返回 (title, preview, element_count)"""
    try:
        c = json.loads(body_raw)
    except Exception:
        return "", "", 0
    title = ""
    try:
        title = c["header"]["title"]["content"]
    except Exception:
        pass
    if not title:
        # post / text
        title = str(c)[:40]
    preview = ""
    els = 0
    try:
        els = len(c["body"]["elements"])
    except Exception:
        els = len(c.get("elements", []))
    try:
        parts = []
        for el in c["body"]["elements"]:
            if isinstance(el, dict):
                t = el.get("content") or el.get("text", {}).get("content") or ""
                if t:
                    parts.append(re.sub(r"\s+", " ", t))
        preview = " ".join(parts)[:200]
    except Exception:
        preview = str(c)[:200]
    return title, preview, els


def is_abnormal(title, preview, msg_type, els):
    reasons = []
    t_low = title.lower()
    for w in BAD_WORDS:
        if w in t_low:
            reasons.append(f"title含{w}字样")
            break
    if not reasons:
        body_text = title + " " + preview
        if any(ok in body_text for ok in OK_WORDS):
            pass
        else:
            for w in BAD_WORDS:
                if w in body_text.lower():
                    reasons.append(f"body含{w}字样")
                    break
    if msg_type == "interactive" and els < 2:
        reasons.append("interactive但elements<2（疑似空卡片）")
    return reasons


def main():
    now = datetime.now(CST)
    audit_date = now.strftime("%Y-%m-%d")
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=55, second=0, microsecond=0)
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())

    token = get_token()
    msgs = fetch_messages(token, start_ts, end_ts)

    ai_msgs = []
    for m in msgs:
        sid = (m.get("sender") or {}).get("id", "")
        if sid != BOT_APP_ID:
            continue
        msg_type = m.get("msg_type", "")
        body_raw = (m.get("body") or {}).get("content", "{}")
        title, preview, els = parse_card(body_raw) if msg_type == "interactive" else ("", str(body_raw)[:200], 0)
        if msg_type in ("text", "post"):
            try:
                c = json.loads(body_raw)
                title = (c.get("text") or str(c.get("title", "")) or "")[:60]
            except Exception:
                title = str(body_raw)[:60]
        ai_msgs.append({
            "message_id": m.get("message_id", ""),
            "create_time": ts_to_str(m.get("create_time", 0)),
            "msg_type": msg_type,
            "title": title,
            "preview": preview,
            "_els": els,
        })

    # 重复刷屏检测：同一 message_id 1 分钟内重复（同标题+100字符内时间）
    abnormal = []
    seen = {}
    for a in ai_msgs:
        reasons = is_abnormal(a["title"], a["preview"], a["msg_type"], a["_els"])
        key = (a["title"].strip(), a["preview"][:60])
        t = datetime.strptime(a["create_time"], "%Y-%m-%d %H:%M:%S")
        if key in seen and abs((t - seen[key]).total_seconds()) <= 60:
            reasons.append("1分钟内重复发送（刷屏）")
        else:
            seen[key] = t
        if reasons:
            abnormal.append({
                "message_id": a["message_id"],
                "create_time": a["create_time"],
                "title": a["title"],
                "preview": a["preview"],
                "reason": "；".join(reasons),
            })

    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"feishu_audit_{now.strftime('%Y%m%d')}.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_date": audit_date,
            "total_ai_messages": len(ai_msgs),
            "abnormal_count": len(abnormal),
            "abnormal": abnormal,
        }, f, ensure_ascii=False, indent=2)

    print(f"审计日期: {audit_date} | AI消息: {len(ai_msgs)} | 异常: {len(abnormal)}")
    print(f"日志: {log_path}")

    if not abnormal:
        return

    rows = ""
    for a in abnormal[:10]:
        rows += f"| {a['create_time'][11:19]} | {a['title'][:20]} | {a['reason']} |\n"
    card = {
        "schema": "2.0",
        "header": {"title": {"tag": "plain_text", "content": "⚠️ 飞书发消息审计 · 异常"}},
        "body": {"elements": [
            {"tag": "markdown", "content": f"**审计日期**: {audit_date}"},
            {"tag": "markdown", "content": f"**AI 消息总数**: {len(ai_msgs)}"},
            {"tag": "markdown", "content": f"**异常数**: {len(abnormal)}"},
            {"tag": "markdown", "content": f"| 时间 | 标题 | 异常原因 |\n|---|---|---|\n{rows}"},
        ]},
    }
    r = send_card(OWNER_OPEN_ID, card)
    print("推送结果:", r.get("code"))


if __name__ == "__main__":
    main()
