#!/opt/homebrew/bin/python3.12
"""
DeepSeek 余额/可用性探针 — 只输出状态与余额数字，绝不回显 key。

用法:
  python3 scripts/deepseek_balance.py

背景（2026-09-16）：cron 大面积 402 Insufficient Balance（fallback 链为空 → chain_exhausted），
需要快速判定「余额是否已恢复」，避免盲目重跑失败任务。

注意：必须显式禁用系统代理（7897 会劫持请求）。
"""

import json
import os
import sys
import urllib.request

API = "https://api.deepseek.com/user/balance"


def effective_key():
    for name in ("DEEPSEEK_API_KEY",):
        v = os.environ.get(name)
        if v:
            return v, f"env:{name}"
    # 回退读 models.json（不打印内容）
    p = os.path.expanduser("~/.openclaw/agents/main/agent/models.json")
    try:
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        import re

        m = re.search(r'"apiKey"\s*:\s*"(sk-[A-Za-z0-9]+)"', txt)
        if m:
            return m.group(1), "models.json"
    except Exception:
        pass
    return None, None


def main():
    key, src = effective_key()
    if not key:
        print("[❌] 未找到 DeepSeek API key（env DEEPSEEK_API_KEY 与 models.json 均无）")
        return 2

    print(f"[🔑] 使用凭据来源: {src}（值已隐去）")

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(API, headers={"Authorization": f"Bearer {key}"})
    try:
        with opener.open(req, timeout=15) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "ignore")[:200]
        except Exception:
            pass
        print(f"[❌] HTTP {e.code} — {body}")
        if e.code == 402:
            print("     → 余额不足，重跑失败任务必然再次失败，需先充值")
        elif e.code == 401:
            print("     → key 无效/被吊销")
        return 1
    except Exception as e:
        print(f"[❌] 请求失败: {e}")
        return 1

    avail = data.get("is_available")
    print(f"[{'✅' if avail else '❌'}] is_available = {avail}")
    for b in data.get("balance_infos", []) or []:
        print(
            f"     {b.get('currency')}: 总额 {b.get('total_balance')}"
            f" | 赠金 {b.get('granted_balance')} | 充值 {b.get('topped_up_balance')}"
        )
    return 0 if avail else 1


if __name__ == "__main__":
    sys.exit(main())
