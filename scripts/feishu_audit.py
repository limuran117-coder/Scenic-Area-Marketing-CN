#!/opt/homebrew/bin/python3.12
"""
飞书发消息审计脚本：拉取电影小镇群 00:00-23:55 的 AI 系统消息，识别异常卡片，写日志
用法: python3 feishu_audit.py [YYYY-MM-DD]
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta

APP_ID = "cli_a941d5340639dcef"
APP_SECRET = "yNMaSBoHmrn9FcsrpWCzlcerQCD5aHji"
API_BASE = "https://open.feishu.cn/open-apis"
CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"  # 电影小镇群
AI_SENDER_ID = "cli_a941d5340639dcef"  # 电影小镇AI发卡AppID
LOG_DIR = "/Users/tianjinzhan/.openclaw/workspace/log"

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

def list_messages(token, start_ms, end_ms):
    """拉取群消息，返回全部消息列表"""
    all_msgs = []
    page_token = None
    while True:
        url = (f"{API_BASE}/im/v1/messages?container_id_type=chat"
               f"&container_id={CHAT_ID}"
               f"&start_time={start_ms}&end_time={end_ms}"
               f"&sort_type=ByCreateTimeDesc&page_size=50")
        if page_token:
            url += f"&page_token={page_token}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            data = json.loads(e.read().decode())
            print(f"❌ HTTP {e.code}: {data}")
            raise
        if data.get("code") != 0:
            print(f"❌ API错误: {data}")
            raise Exception(data)
        items = data.get("data", {}).get("items", [])
        all_msgs.extend(items)
        has_more = data.get("data", {}).get("has_more", False)
        page_token = data.get("data", {}).get("page_token")
        if not has_more or not page_token:
            break
    return all_msgs

def extract_preview(msg):
    """提取卡片 body 前 200 字预览"""
    try:
        content = json.loads(msg.get("body", {}).get("content", "{}"))
    except Exception:
        return ""
    if msg.get("msg_type") == "interactive" or "elements" in content:
        # 卡片：提取 text 内容
        texts = []
        def walk(node):
            if isinstance(node, dict):
                if node.get("tag") == "markdown" and node.get("content"):
                    texts.append(node["content"])
                if node.get("tag") == "plain_text" and node.get("content"):
                    texts.append(node["content"])
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(content)
        return " ".join(texts)[:200]
    return ""

def main():
    # 审计日期
    if len(sys.argv) > 1:
        audit_date = sys.argv[1]
    else:
        audit_date = datetime.now().strftime("%Y-%m-%d")
    # 转时间戳（Asia/Shanghai）
    start_dt = datetime.strptime(audit_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(audit_date + " 23:55:00", "%Y-%m-%d %H:%M:%S")
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)

    token = get_token()
    msgs = list_messages(token, start_ms, end_ms)

    # 筛选 AI 消息
    ai_msgs = [m for m in msgs if m.get("sender", {}).get("id") == AI_SENDER_ID]

    # 识别异常
    abnormal = []
    seen_times = {}
    for m in ai_msgs:
        create_ms = int(m.get("create_time", "0"))
        create_dt = datetime.fromtimestamp(create_ms / 1000)
        create_str = create_dt.strftime("%Y-%m-%d %H:%M:%S")
        mid = m.get("message_id", "")
        mtype = m.get("msg_type", "")
        preview = extract_preview(m)
        title = ""
        try:
            content = json.loads(m.get("body", {}).get("content", "{}"))
            title = content.get("header", {}).get("title", {}).get("content", "")
        except Exception:
            pass

        reasons = []
        # 标题含测试字样
        combined_title = title
        if any(k in combined_title for k in ["test", "TEST", "测试", "调试", "debug", "dry-run", "占位"]):
            reasons.append("title含test/测试字样")
        # body 含 test/测试（排除合规"测试结果"）
        body_low = preview.lower()
        if ("test" in body_low or "测试" in preview) and "测试结果" not in preview:
            reasons.append("body含test/测试")
        # interactive 但 elements < 2
        if mtype == "interactive":
            try:
                el_count = len(content.get("body", {}).get("elements", []))
            except Exception:
                el_count = 0
            if el_count < 2:
                reasons.append("空卡片(elements<2)")
        # 1分钟内重复
        if create_ms in seen_times:
            reasons.append("1分钟内重复发送")
        seen_times.setdefault(create_ms, 0)
        seen_times[create_ms] += 1

        if reasons:
            abnormal.append({
                "message_id": mid,
                "create_time": create_str,
                "title": title,
                "preview": preview[:200],
                "reason": "；".join(reasons)
            })

    total = len(ai_msgs)
    result = {
        "audit_date": audit_date,
        "total_ai_messages": total,
        "abnormal_count": len(abnormal),
        "abnormal": abnormal
    }

    # 写日志
    log_path = f"{LOG_DIR}/feishu_audit_{audit_date.replace('-','')}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 审计完成: total={total}, abnormal={len(abnormal)}")
    print(f"日志: {log_path}")

    # 输出异常给调用方（JSON stdout）
    print("---RESULT_JSON---")
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
