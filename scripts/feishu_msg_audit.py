#!/opt/homebrew/bin/python3.12
"""飞书发消息审计 - 拉取指定时间窗内 AI 系统消息并识别异常卡片"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/Users/tianjinzhan/.openclaw/workspace/scripts")
from send_feishu_card import get_token, API_BASE

CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"
AI_SENDER = "cli_a941d5340639dcef"
CST = timezone(timedelta(hours=8))


def api_get(path, token, params):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{API_BASE}{path}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_messages(token, start_ts, end_ts):
    msgs = []
    page_token = None
    while True:
        params = {
            "container_id_type": "chat",
            "container_id": CHAT_ID,
            "start_time": str(start_ts),
            "end_time": str(end_ts),
            "sort_type": "ByCreateTimeDesc",
            "page_size": "50",
        }
        if page_token:
            params["page_token"] = page_token
        data = api_get("/im/v1/messages", token, params)
        if data.get("code") != 0:
            print(f"❌ API错误: {data}")
            break
        d = data.get("data", {})
        msgs.extend(d.get("items", []))
        if d.get("has_more") and d.get("page_token"):
            page_token = d["page_token"]
        else:
            break
    return msgs


BAD_TOKENS = ["test", "测试", "调试", "debug", "dry-run", "dry_run", "占位"]


PLACEHOLDER = "请升级至最新版本客户端"


def flatten_els(els):
    """展平 elements（可能是嵌套 list），提取 text/content/img 标记"""
    parts = []
    imgs = 0
    for el in els or []:
        if isinstance(el, list):
            sub, n = flatten_els(el)
            parts.extend(sub)
            imgs += n
        elif isinstance(el, dict):
            if el.get("tag") == "img":
                imgs += 1
            txt = el.get("content") or el.get("text") or ""
            if txt:
                parts.append(str(txt))
    return parts, imgs


def analyze(msgs):
    ai_msgs = []
    abnormal = []
    for m in msgs:
        sender = (m.get("sender") or {}).get("id", "")
        if sender != AI_SENDER:
            continue
        msg_type = m.get("msg_type", "")
        try:
            body = json.loads(m.get("body", {}).get("content", "{}"))
        except Exception:
            body = {}
        title = ""
        preview = ""
        els = []
        n_img = 0
        if msg_type == "interactive":
            card = body
            if isinstance(body, dict) and "card" in body and isinstance(body["card"], dict):
                card = body["card"]
            # header.title（schema 2.0 完整卡片）或 body.title（API 摘要形式）
            title = (((card.get("header") or {}).get("title") or {}).get("content") or "") \
                or str(card.get("title") or "")
            els = ((card.get("body") or {}).get("elements")) or card.get("elements") or []
            parts, n_img = flatten_els(els)
            preview = " | ".join(p for p in parts if PLACEHOLDER not in p)[:200]
        elif msg_type == "text":
            preview = str(body.get("text", ""))[:200]
        elif msg_type == "post":
            preview = json.dumps(body, ensure_ascii=False)[:200]
            parts, n_img = flatten_els([body])
            preview = " | ".join(p for p in parts if PLACEHOLDER not in p)[:200] or preview

        ts = int(m.get("create_time", "0")) / 1000
        ct = datetime.fromtimestamp(ts, CST).strftime("%Y-%m-%d %H:%M:%S")
        rec = {
            "message_id": m.get("message_id", ""),
            "create_time": ct,
            "msg_type": msg_type,
            "title": title,
            "preview": preview,
            "elements_count": (len(els) if msg_type == "interactive" and isinstance(els, list) else None),
            "has_content": bool(title or preview or n_img),
        }
        ai_msgs.append(rec)

        reasons = []
        low_t = title.lower()
        if any(t in low_t for t in BAD_TOKENS):
            reasons.append(f"title含异常字样: {title}")
        low_p = preview.lower()
        if any(t in low_p for t in BAD_TOKENS) and "测试结果" not in preview:
            reasons.append("body含异常字样")
        # 仅当标题/正文/图片全空才判空卡片（API 对 interactive 卡片返回
        # "请升级至最新版本客户端" 占位，不能只看 elements 数量）
        if msg_type == "interactive" and not rec["has_content"]:
            reasons.append("空卡片(无标题/正文/图片)")
        if reasons:
            abnormal.append({**rec, "reason": "; ".join(reasons)})

    # 重复刷屏检测
    seen = {}
    for r in ai_msgs:
        key = (r["title"], r["preview"])
        seen.setdefault(key, []).append(r)
    for key, group in seen.items():
        if len(group) > 1 and all(g["has_content"] for g in group):
            times = [datetime.strptime(g["create_time"], "%Y-%m-%d %H:%M:%S") for g in group]
            times.sort()
            if (times[-1] - times[0]).total_seconds() <= 60:
                for g in group[1:]:
                    abnormal.append({**g, "reason": "1分钟内重复发送(刷屏)"})
    return ai_msgs, abnormal


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now(CST).strftime("%Y-%m-%d")
    start = int(datetime.strptime(day + " 00:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=CST).timestamp())
    end = int(datetime.now(CST).timestamp())
    print(f"🕐 窗口: {day} 00:00:00 → {datetime.now(CST).strftime('%H:%M:%S')}")
    token = get_token()
    msgs = fetch_messages(token, start, end)
    print(f"📨 群消息总数: {len(msgs)}")
    ai_msgs, abnormal = analyze(msgs)
    print(f"🤖 AI 消息数: {len(ai_msgs)}   ⚠️ 异常: {len(abnormal)}")
    result = {
        "audit_date": day,
        "total_ai_messages": len(ai_msgs),
        "abnormal_count": len(abnormal),
        "abnormal": abnormal,
    }
    out = f"/Users/tianjinzhan/.openclaw/workspace/log/feishu_audit_{day.replace('-','')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 已写入 {out}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
