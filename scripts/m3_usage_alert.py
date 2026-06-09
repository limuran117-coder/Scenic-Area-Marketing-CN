#!/usr/bin/env python3
"""
m3_usage_alert.py — M3 token 用量预警（飞书卡片版）

从 m3_usage.py 的输出提取用量百分比，按阈值发飞书告警。
- ≥90%：发电影小镇群（重要）
- ≥70%：发电影小镇群（警告）
- <70%：静默，不推送
"""
import json, subprocess, re, os, sys
from datetime import datetime

import urllib.request
import urllib.error

WEBHOOK_FILE = os.path.expanduser("~/.hermes/state/feishu_webhook.json")

def get_m3_usage_pct():
    """调 m3_usage.py 拿到百分比"""
    p = subprocess.run(
        ["python3", "/Users/tianjinzhan/.hermes/hermes-agent/openclaw-watch/bin/m3_usage.py"],
        capture_output=True, text=True, timeout=30
    )
    out = p.stdout
    m = re.search(r'5h 窗口用量: ([\d,]+) / ([\d,]+) = ([\d.]+)%', out)
    if not m:
        return None, None, None
    used = int(m.group(1).replace(",", ""))
    limit = int(m.group(2).replace(",", ""))
    pct = float(m.group(3))
    # reset 时间
    rm = re.search(r'重置时间: (.+)', out)
    reset = rm.group(1).strip() if rm else ""
    return used, limit, pct, reset

def send_feishu(card):
    """发飞书卡片到电影小镇群"""
    # 飞书 webhook 这里用 openclaw 内置通道
    # 直接用 send_feishu_card.py 模式
    APP_ID = "cli_a941d5340639dcef"
    APP_SECRET_PATH = os.path.expanduser("~/.openclaw/workspace/.secrets/feishu_secret")
    chat_id = "oc_2581c03b79e4893cc3616b253d60f34e"
    # 走 openclaw 的 message 工具不行（cron 没这个工具）
    # 改用直接调 openclaw 的发送命令
    import tempfile
    jf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(card, jf, ensure_ascii=False)
    jf.close()
    # 读 JSON 内容（不依赖 shell 解析）
    with open(jf.name) as f:
        card_json = f.read()
    p = subprocess.run(
        ["python3", "/Users/tianjinzhan/.openclaw/workspace/scripts/send_feishu_card.py",
         chat_id, card_json],
        capture_output=True, text=True, timeout=30
    )
    os.unlink(jf.name)
    return p.returncode, p.stdout, p.stderr

def main():
    result = get_m3_usage_pct()
    if result[0] is None:
        print(f"[{datetime.now():%H:%M}] 无法解析 m3_usage.py 输出，跳过")
        return 0
    
    used, limit, pct, reset = result
    
    print(f"[{datetime.now():%H:%M}] M3 用量: {used:,}/{limit:,} = {pct:.1f}% (reset {reset})")
    
    # 阈值判断
    if pct < 70:
        print("  静默（<70%）")
        return 0
    elif pct < 90:
        level = "🟠 警告"
        title = f"M3 5h 配额 {pct:.0f}% 触发预警"
    else:
        level = "🔴 严重"
        title = f"M3 5h 配额 {pct:.0f}% 即将/已触顶"
    
    # 算还能跑多少任务（按 200K/task 估算）
    remain_pct = 100 - pct
    est_tokens = int(limit * remain_pct / 100)
    est_tasks = est_tokens // 200_000
    
    md = f"""**{level}** M3 5h token 窗口

| 指标 | 值 |
|---|---|
| 已用 | {used:,} / {limit:,} tokens |
| 占比 | **{pct:.1f}%** |
| 重置 | {reset} |
| 剩余可跑 | ≈ {est_tasks} 个任务（按 200K/任务估） |

💡 建议
- 撞限任务没成功 = **等限额接触后补发即可**（不算失败）
- 预算问题站长会自己处理（升套餐 / 调限额）
- AI 不为配额妥协任务质量 / 错峰 / 减频"""
    
    # 6/9 18:21 站长确认：M3 配额告警**不发到电影小镇群**（业务群不污染）
    # 改成静默执行：只打日志记录，不推送飞书
    print(f"  [告警静默] {level} M3 配额 {pct:.1f}% 触碰阈值（不发群，记录到日志）")
    return 0
    
    # 以下代码保留但不再执行（防止后续站长改变主意想发）
    card = {
        "schema": "2.0",
        "header": {"title": {"tag": "plain_text", "content": title}},
        "body": {"elements": [{"tag": "markdown", "content": md}]}
    }

if __name__ == "__main__":
    sys.exit(main())
