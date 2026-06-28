#!/opt/homebrew/bin/python3.12
"""
每日复盘 - 投递阶段脚本（2026-06-22 W26 新增，配套方案 A #2）
- 读 /tmp/daily_recap_<YYYY-MM-DD>.json
- 用 send_feishu_card.py 投递到电影小镇群
- 失败时重试 3 次（间隔 10s/30s/60s）
- 仍失败则：保留 /tmp 文件 + 推飞书私聊给站长

用法:
  python3 scripts/daily_recap_deliver.py                    # 自动用今天日期
  python3 scripts/daily_recap_deliver.py 2026-06-21         # 指定日期
  python3 scripts/daily_recap_deliver.py --no-retry         # 不重试（cron 5min 调度时由 cron 自己重试）
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 配置
CHAT_ID = "oc_2581c03b79e4893cc3616b253d60f34e"
ADMIN_ID = "ou_f308d672765ecf1be73a75eb5e5f0f48"  # 站长私聊
SEND_SCRIPT = "/Users/tianjinzhan/.openclaw/workspace/scripts/send_feishu_card.py"
RECAP_DIR = Path("/tmp")
RETRY_DELAYS = [0, 10, 30, 60]  # 重试间隔（秒）


def find_latest_recap(target_date: str = None) -> Path:
    """找最新的复盘 JSON"""
    if target_date:
        path = RECAP_DIR / f"daily_recap_{target_date}.json"
        if path.exists():
            return path
        print(f"❌ 指定日期文件不存在: {path}")
        sys.exit(1)
    # 否则找最新的
    files = sorted(RECAP_DIR.glob("daily_recap_*.json"), reverse=True)
    if not files:
        print("❌ /tmp/ 下没有 daily_recap_*.json 文件")
        sys.exit(1)
    return files[0]


def send_card(card_path: Path) -> dict:
    """调 send_feishu_card.py 投递

    send_feishu_card.py 期望 argv[2] 是 JSON 字符串本身（不是路径），
    所以这里先读文件再把内容传出去。
    """
    try:
        card_json = card_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"ok": False, "returncode": -1, "error": f"read card file failed: {e}"}
    try:
        result = subprocess.run(
            ["python3", SEND_SCRIPT, CHAT_ID, card_json],
            capture_output=True, text=True, timeout=30,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[:300],
            "stderr": result.stderr[:300],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": -1, "error": "timeout 30s"}
    except Exception as e:
        return {"ok": False, "returncode": -1, "error": str(e)}


def send_admin_alert(reason: str, card_path: Path):
    """给站长私聊推送告警"""
    msg = f"⚠️ 每日复盘卡片投递失败\n\n原因：{reason}\n卡片文件：{card_path}\n\n请手动重投或检查飞书 API。\n\n手动重投命令：\npython3 {SEND_SCRIPT} {CHAT_ID} {card_path}"
    # 用最简 text message 走 API
    import urllib.request
    try:
        token_req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            data=json.dumps({"app_id": "cli_a941d5340639dcef", "app_secret": "yNMaSB…aHji"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        token = json.loads(urllib.request.urlopen(token_req, timeout=8).read())["tenant_access_token"]
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        data = json.dumps({
            "receive_id": ADMIN_ID,
            "msg_type": "text",
            "content": json.dumps({"text": msg}),
        }).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })
        urllib.request.urlopen(req, timeout=8).read()
        print("✅ 已推私聊告警")
    except Exception as e:
        print(f"❌ 私聊告警也失败: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?", help="复盘日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--no-retry", action="store_true", help="不重试（cron 5min 调度时由 cron 自己重试）")
    args = parser.parse_args()

    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    card_path = find_latest_recap(target_date if args.date else None)
    print(f"[投递] {datetime.now().strftime('%H:%M:%S')} 目标: {CHAT_ID}")
    print(f"[投递] 卡片文件: {card_path} ({card_path.stat().st_size} bytes)")

    if args.no_retry:
        # 单次投递
        result = send_card(card_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["ok"] else 1)

    # 重试模式
    delays = RETRY_DELAYS if args.date else [0]  # cron 模式下只投一次（cron 5min 重启）
    last_err = ""
    for attempt, delay in enumerate(delays):
        if delay > 0:
            print(f"[重试] 第 {attempt+1}/{len(delays)} 次，等待 {delay}s...")
            time.sleep(delay)
        result = send_card(card_path)
        if result["ok"]:
            print(f"✅ 投递成功（第 {attempt+1} 次）")
            return 0
        last_err = result.get("stderr") or result.get("error") or "unknown"
        print(f"❌ 第 {attempt+1} 次失败: {last_err[:100]}")

    # 全部失败
    print(f"\n🚨 4 次投递全部失败")
    print(f"最后错误: {last_err}")
    send_admin_alert(last_err, card_path)
    sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())