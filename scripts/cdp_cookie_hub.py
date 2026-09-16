#!/opt/homebrew/bin/python3.12
"""
CDP Cookie 总控中心 — 从已登录的专属浏览器(端口18800)批量同步所有服务的Cookie

用法:
  python3 scripts/cdp_cookie_hub.py            # 同步所有服务（默认）
  python3 scripts/cdp_cookie_hub.py --check    # 只检查登录状态，不同步
  python3 scripts/cdp_cookie_hub.py douyin     # 只同步抖音
  python3 scripts/cdp_cookie_hub.py xiaohongshu # 只同步小红书

原理:
  专属浏览器(CDP端口18800)的所有Tab共享一个浏览器上下文，Cookie存于同一 Profile。
  本工具通过 CDP 提取该 Profile 的全部 Cookie，按服务分文件存储。

⚠️ 2026-09-16 重要修复（Chrome 152 兼容）：
  1) **浏览器级 WS（/json/version 的 webSocketDebuggerUrl）调 `Storage.getCookies`
     会被拒**：`Browser context management is not supported.`
     → 必须改用 **page target 级 WS**（/json/list 里任一 type=page 的端点），
       同一方法实测可正常返回全部 Cookie（369 条）。
  2) **不再预处理关闭标签页**。旧版 `clear_browser_tabs()` 是为绕 Playwright 初始化
     死锁，但它每天 08:05 把浏览器标签全清空 → 次日 07:30 前浏览器长期 0 标签页，
     是「登录态上下文丢失」的直接成因。WS 路径无此问题。
  3) Playwright `connect_over_cdp` 保留为兜底路径（Chrome 152 上时好时坏，
     报 `Browser.setDownloadBehavior: Browser context management is not supported`）。

输出:
  /tmp/juLiang_cookies.json       → 抖音(+竞品关键词脚本共用)
  /tmp/xiaohongshu_cookies.json   → 小红书
  /tmp/weibo_cookies.json         → 微博(预留)

被哪些脚本使用:
  - douyin_index.py          读 /tmp/juLiang_cookies.json (备选)
  - competitor_keyword_v8.py    读 /tmp/juLiang_cookies.json
  - competitor_keyword_index.py 读 /tmp/juLiang_cookies.json
  - xiaohongshu_crawl.py        直接CDP，无需Cookie文件(但做备份)
"""

import asyncio
import datetime
import json
import os
import sys
import urllib.request

CDP_HOST = "http://127.0.0.1:18800"

# 各服务的Cookie域名过滤规则
SERVICES = {
    "douyin": {
        "file": "/tmp/juLiang_cookies.json",
        "domains": ["douyin.com", "bytedance.com", "ixigua.com"],
        "label": "🎬 抖音",
        "min_cookies": 5,
    },
    "xiaohongshu": {
        "file": "/tmp/xiaohongshu_cookies.json",
        "domains": ["xiaohongshu.com"],
        "label": "📕 小红书",
        "min_cookies": 3,
    },
    "weibo": {
        "file": "/tmp/weibo_cookies.json",
        "domains": ["weibo.com", "sina.com.cn"],
        "label": "🐦 微博",
        "min_cookies": 3,
    },
}

EXPIRED_FLAGS = [
    "/tmp/douyin_cookie_expired.flag",
    "/tmp/xiaohongshu_cookie_expired.flag",
]


def _opener():
    """⚠️ 必须绕过系统代理：macOS 系统代理(7897)不含 127.0.0.1 例外，
    默认 urllib 会读系统代理 → 访问本机 CDP 返回 502（2026-09-12 实测）。"""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _http_json(path, timeout=8):
    with _opener().open(f"{CDP_HOST}{path}", timeout=timeout) as r:
        return json.load(r)


def _page_ws_url():
    """取任一 page target 的 WS URL（Chrome 152 必须走 page 级）。"""
    try:
        targets = _http_json("/json/list", timeout=8)
    except Exception as e:
        print(f"[⚠️] /json/list 不可达: {e}")
        return None
    for t in targets or []:
        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
            return t["webSocketDebuggerUrl"]
    return None


async def _ws_fetch_cookies():
    """路径 A（首选）：page target 级 CDP WebSocket 调 Storage.getCookies。"""
    import websockets

    ws_url = _page_ws_url()
    if not ws_url:
        raise RuntimeError("没有可用的 page target（浏览器 0 标签页）")

    async with websockets.connect(ws_url, open_timeout=15, max_size=None) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Storage.getCookies"}))
        while True:
            msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=25))
            if msg.get("id") == 1:
                if "error" in msg:
                    raise RuntimeError(f"Storage.getCookies 失败: {msg['error']}")
                return msg["result"].get("cookies", [])


async def _playwright_fetch_cookies():
    """路径 B（兜底）：Playwright connect_over_cdp（Chrome 152 上不稳定）。"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_HOST, timeout=20000)
        if not browser.contexts:
            raise RuntimeError("浏览器无可用上下文")
        return await browser.contexts[0].cookies()


def fetch_cookies(use_playwright=False):
    if use_playwright:
        print("[🔗] 路径 B: Playwright ...", end=" ", flush=True)
        cookies = asyncio.run(_playwright_fetch_cookies())
    else:
        print("[🔗] 路径 A: page-target WebSocket ...", end=" ", flush=True)
        cookies = asyncio.run(_ws_fetch_cookies())
    print(f"✅ {len(cookies)} 条")
    return cookies


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    check_only = "--check" in flags
    force_playwright = "--playwright" in flags

    services = {k: v for k, v in SERVICES.items() if k in args} if args else SERVICES
    if not services:
        print(f"[❌] 未找到匹配的服务。可用: {', '.join(SERVICES.keys())}")
        return 1

    print("=" * 55)
    print(f"  CDP Cookie 总控中心 — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  浏览器: chrome (端口 18800)")
    print(f"  目标: {'全部' if not args else ', '.join(args)}")
    print("=" * 55)

    try:
        cookies = fetch_cookies(use_playwright=force_playwright)
    except Exception as e:
        if not force_playwright:
            print(f"❌ ({e})")
            print("[↩️] 回退尝试 Playwright ...")
            try:
                cookies = fetch_cookies(use_playwright=True)
            except Exception as e2:
                print(f"\n[❌] 两条路径均失败: {e2}")
                print("  请确认: 1) 专属浏览器已开 2) 18800 已启动 3) 各 Tab 已登录")
                return 1
        else:
            print(f"\n[❌] 连接失败: {e}")
            print("  请确认: 1) 专属浏览器已开 2) 18800 已启动 3) 各 Tab 已登录")
            return 1

    all_ok = True
    for key, svc in services.items():
        matched = [
            c
            for c in cookies
            if any(d in (c.get("domain") or "") for d in svc["domains"])
        ]
        if len(matched) >= svc["min_cookies"]:
            if check_only:
                print(f"  {svc['label']}: ✅ {len(matched)} 条 Cookie — 登录有效")
            else:
                fp = svc["file"]
                os.makedirs(os.path.dirname(fp) or ".", exist_ok=True)
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(matched, f, ensure_ascii=False, indent=2)
                print(f"  {svc['label']}: ✅ {len(matched)} 条 Cookie → {fp}")
        else:
            print(f"  {svc['label']}: ⚠️ 仅 {len(matched)} 条 Cookie (需≥{svc['min_cookies']}) — 可能未登录")
            all_ok = False

    if check_only:
        print("\n📊 检查完成")
    else:
        for flag in EXPIRED_FLAGS:
            if os.path.exists(flag):
                os.remove(flag)
                print(f"  [🧹] 清除过期标记: {flag}")
        print("\n✅ 全部同步完成!" if all_ok else "\n⚠️ 部分服务未登录，已同步可用项")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
