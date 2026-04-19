#!/usr/bin/env python3
"""
飞书卡片发送脚本（防错版）
用法: python3 send_feishu_card.py <chat_id> <card_json>
示例: python3 send_feishu_card.py oc_xxx '{"schema":"2.0","header":...}'

⚠️ 格式规范（2026-04-19确认）：
  - header.title 必须是 {"tag": "plain_text", "content": "..."}
  - 内容放 body.elements[]（不是根级 elements[]）
  - 每个 markdown 元素必须内容完整（表头+表格放一起，不能拆分）
  - 符号用 ↓↑，异动用 🔺
"""
import json
import sys
import urllib.request

APP_ID = "cli_a941d5340639dcef"
APP_SECRET = "yNMaSBoHmrn9FcsrpWCzlcerQCD5aHji"
API_BASE = "https://open.feishu.cn/open-apis"

def validate_card(card):
    """发送前检查卡片格式，发现问题警告但不阻止发送"""
    errors = []
    warnings = []

    # 检查 schema
    if card.get("schema") != "2.0":
        warnings.append("缺少 schema: '2.0'，可能导致渲染异常")

    # 检查 header.title 格式
    header = card.get("header", {})
    title = header.get("title", {})
    if not isinstance(title, dict) or title.get("tag") != "plain_text":
        errors.append("header.title 必须是 {'tag': 'plain_text', 'content': '...'}，当前: " + str(title))

    # 检查 body.elements
    body = card.get("body", {})
    elements = body.get("elements")
    if not elements:
        errors.append("body.elements 不存在或为空")
    elif not isinstance(elements, list):
        errors.append("body.elements 必须是数组")
    elif len(elements) < 4:
        warnings.append(f"elements 只有 {len(elements)} 个，内容可能不完整（建议≥4个分段）")
    elif len(elements) > 15:
        warnings.append(f"elements 有 {len(elements)} 个，可能过多")

    # 检查是否用错了根级 elements
    if "elements" in card and "body" not in card:
        errors.append("检测到根级 elements，请改为 body.elements[]，否则渲染异常")

    # 检查 markdown 元素内容是否太碎（表格被拆开）
    for i, el in enumerate(elements or []):
        if el.get("tag") == "markdown":
            content = el.get("content", "")
            # 如果内容包含表格分隔符 | 但没有表头行，疑似被拆散
            if "|--" in content and "景区" not in content and "搜索指数" not in content:
                warnings.append(f"第 {i+1} 个 element 含有表格分隔符但无表头，可能是表格被拆散了")

    if errors:
        print("❌ 格式错误:")
        for e in errors:
            print(f"   {e}")
    if warnings:
        print("⚠️ 格式警告:")
        for w in warnings:
            print(f"   {w}")
    return len(errors) == 0

def get_token():
    url = f"{API_BASE}/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})
    req = urllib.request.Request(url, data=payload.encode(),
                                headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return data["tenant_access_token"]

def send_card(chat_id, card, skip_validation=False):
    if not skip_validation:
        print(f"📋 正在验证卡片格式（{len(card.get('body',{}).get('elements',[]))} 个元素）...")
        validate_card(card)
        print()

    token = get_token()
    url = f"{API_BASE}/im/v1/messages?receive_id_type=chat_id"
    payload = json.dumps({
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False)
    }, ensure_ascii=False)
    req = urllib.request.Request(url, data=payload.encode("utf-8"),
                                headers={
                                    "Authorization": f"Bearer {token}",
                                    "Content-Type": "application/json"
                                }, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    if result.get("code") == 0:
        print(f"✅ 发送成功: {result['data']['message_id']}")
    else:
        print(f"❌ 发送失败: {result}")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    chat_id = sys.argv[1]
    card = json.loads(sys.argv[2])
    skip_validation = "--force" in sys.argv
    send_card(chat_id, card, skip_validation=skip_validation)
