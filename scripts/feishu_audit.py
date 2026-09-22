#!/opt/homebrew/bin/python3.12
"""飞书发消息审计：拉取当日群消息，筛选 AI 消息，识别异常卡片，写日志。"""
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_feishu_card import APP_ID, API_BASE, get_token

CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"
OWNER_OPEN_ID = "ou_f308d672765ecf1be73a75eb5e5f0f48"
LOG_DIR = os.path.expanduser("~/.openclaw/workspace/log")
CST = timezone(timedelta(hours=8))


def api_get(path, params, token):
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_messages(token):
    start = int(datetime.now(CST).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end = start + 23 * 3600 + 55 * 60
    msgs, page_token = [], None
    while True:
        params = {
            "container_id_type": "chat",
            "container_id": CHAT_ID,
            "start_time": start,
            "end_time": end,
            "sort_type": "ByCreateTimeDesc",
            "page_size": 50,
        }
        if page_token:
            params["page_token"] = page_token
        data = api_get("/im/v1/messages", params, token)
        if data.get("code") != 0:
            raise Exception(f"拉取消息失败: {data}")
        d = data.get("data", {})
        msgs.extend(d.get("items", []))
        if not d.get("has_more"):
            break
        page_token = d.get("page_token")
        if not page_token:
            break
    return msgs


def ts_str(ms):
    return datetime.fromtimestamp(int(ms) / 1000, CST).strftime("%Y-%m-%d %H:%M:%S")


PLACEHOLDER = re.compile(r"请升级至最新版本客户端")


def _walk_text(node, chunks):
    if isinstance(node, str):
        chunks.append(node)
    elif isinstance(node, dict):
        for k in ("content", "text"):
            v = node.get(k)
            if isinstance(v, str):
                chunks.append(v)
        for v in node.values():
            if isinstance(v, (dict, list)):
                _walk_text(v, chunks)
    elif isinstance(node, list):
        for v in node:
            _walk_text(v, chunks)


def card_parts(msg):
    """返回 (title, preview, n_elements, readable)

    readable=False 表示飞书 API 未返回卡片正文（仅占位符），
    此时跳过正文类异常判定，避免误报。
    """
    title, preview, n, readable = "", "", None, True
    try:
        body = json.loads(msg.get("body", {}).get("content", "{}"))
    except Exception:
        return title, preview, n, readable
    if msg.get("msg_type") == "interactive":
        card = body if isinstance(body, dict) else {}
        # 标题：顶层 title 或 header.title.content
        t = card.get("title")
        if isinstance(t, str) and t:
            title = t
        else:
            header = card.get("header", {}) or {}
            ht = header.get("title", {}) or {}
            title = ht.get("content", "") if isinstance(ht, dict) else str(ht)
        elements = ((card.get("body") or {}).get("elements")) or card.get("elements") or []
        # 展平嵌套列表后统计卡片元素数
        flat = []
        for el in elements if isinstance(elements, list) else []:
            flat.extend(el if isinstance(el, list) else [el])
        n = len(flat)
        chunks = []
        _walk_text(flat, chunks)
        chunks = [c for c in chunks if c and not PLACEHOLDER.search(c)]
        preview = re.sub(r"\s+", " ", " ".join(chunks))[:200]
        if not preview and len(chunks) == 0:
            # 正文全为占位符 → 不可读
            raw_chunks = []
            _walk_text(flat, raw_chunks)
            if any(PLACEHOLDER.search(c) for c in raw_chunks):
                readable = False
    elif msg.get("msg_type") == "text":
        txt = body.get("text", "") if isinstance(body, dict) else ""
        preview = txt[:200]
    else:
        preview = json.dumps(body, ensure_ascii=False)[:200]
    return title, preview, n, readable


BAD_TITLE = re.compile(r"test|TEST|测试|调试|debug|dry-run|dryrun|占位", re.I)
BAD_BODY = re.compile(r"\btest\b|TEST|测试|调试|debug|dry-run|占位")
OK_BODY = re.compile(r"测试结果|压力测试|实测|检测|测试点|A/B测试")


def main():
    token = get_token()
    msgs = fetch_messages(token)
    ai = [m for m in msgs if (m.get("sender") or {}).get("id") == APP_ID]

    abnormal = []
    seen = {}
    for m in ai:
        mid = m.get("message_id")
        ct = int(m.get("create_time", 0))
        title, preview, n, readable = card_parts(m)
        reasons = []
        if title and BAD_TITLE.search(title):
            reasons.append("title含test/测试/调试字样")
        if readable and preview and BAD_BODY.search(preview) and not OK_BODY.search(preview):
            reasons.append("正文含test/测试字样")
        if readable and m.get("msg_type") == "interactive" and n is not None and n < 2:
            reasons.append(f"interactive卡片elements={n}(<2疑似空卡片)")
        key = (title[:40], preview[:60])
        if key in seen and abs(ct - seen[key]) <= 60000:
            reasons.append("1分钟内重复内容刷屏")
        seen[key] = ct
        if reasons:
            abnormal.append({
                "message_id": mid,
                "create_time": ts_str(ct),
                "title": title,
                "preview": preview,
                "reason": "; ".join(reasons),
            })

    today = datetime.now(CST).strftime("%Y%m%d")
    report = {
        "audit_date": datetime.now(CST).strftime("%Y-%m-%d"),
        "total_ai_messages": len(ai),
        "abnormal_count": len(abnormal),
        "abnormal": abnormal,
    }
    os.makedirs(LOG_DIR, exist_ok=True)
    path = os.path.join(LOG_DIR, f"feishu_audit_{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
