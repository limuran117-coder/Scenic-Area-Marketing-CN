#!/opt/homebrew/bin/python3.12
"""
CDP Cookie 总控中心 — 从已登录的专属浏览器(端口18800)批量同步所有服务的Cookie

用法:
  python3 scripts/cdp_cookie_hub.py            # 同步所有服务（默认）
  python3 scripts/cdp_cookie_hub.py --check    # 只检查登录状态，不同步
  python3 scripts/cdp_cookie_hub.py douyin     # 只同步抖音
  python3 scripts/cdp_cookie_hub.py xiaohongshu # 只同步小红书

原理:
  专属浏览器(CDP端口18800)的所有Tab共享一个浏览器上下文。
  用户在各Tab已登录的服务(抖音/小红书/微博)，Cookie都在同一个SQLite数据库里。
  本工具通过CDP从运行中的浏览器提取所有域的实时Cookie，按服务分文件存储。

输出:
  /tmp/juLiang_cookies.json       → 抖音(+竞品关键词脚本共用)
  /tmp/xiaohongshu_cookies.json   → 小红书
  /tmp/weibo_cookies.json         → 微博(预留)

被哪些脚本使用:
  - douyin_index_v9.py          读 /tmp/juLiang_cookies.json (备选)
  - competitor_keyword_v8.py    读 /tmp/juLiang_cookies.json
  - competitor_keyword_index.py 读 /tmp/juLiang_cookies.json
  - xiaohongshu_crawl.py        直接CDP，无需Cookie文件(但做备份)
"""

import json
import datetime
import sys
import os

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


async def sync_all_cookies(targets=None, check_only=False):
    """连接CDP浏览器，提取所有服务的Cookie"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[❌] playwright 未安装，无法连接CDP浏览器")
        return False

    services_to_run = SERVICES
    if targets:
        services_to_run = {k: v for k, v in SERVICES.items() if k in targets}

    if not services_to_run:
        print(f"[❌] 未找到匹配的服务。可用: {', '.join(SERVICES.keys())}")
        return False

    print("=" * 55)
    print(f"  CDP Cookie 总控中心 — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  浏览器: chrome (端口 18800)")
    print(f"  目标: {'全部' if not targets else ', '.join(targets)}")
    print("=" * 55)

    try:
        async with async_playwright() as p:
            print(f"\n[🔗] 连接浏览器 {CDP_HOST} ...", end=" ", flush=True)
            browser = await p.chromium.connect_over_cdp(CDP_HOST)
            print("✅ 成功")

            # 获取浏览器上下文
            if hasattr(browser, "contexts") and browser.contexts:
                context = browser.contexts[0]
            else:
                print("[❌] 浏览器无可用上下文")
                return False

            # 列出当前打开的Tab
            tab_count = len(context.pages) if hasattr(context, "pages") else 0
            print(f"[📑] 浏览器当前 {tab_count} 个Tab")
            for i, pg in enumerate(
                context.pages if hasattr(context, "pages") else []
            ):
                try:
                    url = pg.url[:80] if pg.url else "(无)"
                    print(f"      Tab{i}: {url}")
                except Exception:
                    print(f"      Tab{i}: (无法获取)")

            # 获取所有Cookie
            print(f"\n[🍪] 正在提取浏览器Cookie...", end=" ", flush=True)
            raw_cookies = await context.cookies()
            print(f"共 {len(raw_cookies)} 条")

            # 按服务分组
            all_ok = True
            for service_key, service in services_to_run.items():
                matched = [
                    c
                    for c in raw_cookies
                    if any(
                        domain in (c.get("domain", "") or "")
                        for domain in service["domains"]
                    )
                ]

                tag = service["label"]
                min_cnt = service["min_cookies"]

                if len(matched) >= min_cnt:
                    if check_only:
                        print(f"  {tag}: ✅ {len(matched)}条Cookie — 登录有效")
                    else:
                        # 保存到文件
                        filepath = service["file"]
                        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(matched, f, ensure_ascii=False, indent=2)
                        print(
                            f"  {tag}: ✅ {len(matched)}条Cookie → {filepath}"
                        )
                else:
                    print(
                        f"  {tag}: ⚠️ 仅 {len(matched)}条Cookie (需≥{min_cnt}) — 可能未登录"
                    )
                    all_ok = False

            # 输出摘要
            if check_only:
                print(f"\n📊 检查完成")
            else:
                # 清除Cookie过期标记
                for flag in [
                    "/tmp/douyin_cookie_expired.flag",
                    "/tmp/xiaohongshu_cookie_expired.flag",
                ]:
                    if os.path.exists(flag):
                        os.remove(flag)
                        print(f"  [🧹] 清除过期标记: {flag}")
                print(f"\n✅ 全部同步完成!")

            return all_ok

    except Exception as e:
        print(f"\n[❌] 连接失败: {e}")
        print("  请确认:")
        print("  1. 专属浏览器(Chrome)已打开")
        print("  2. 端口18800已启动")
        print("  3. 各Tab已登录相应服务")
        return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]  # positional
    flags = [a for a in sys.argv[1:] if a.startswith("--")]     # flags

    check_only = "--check" in flags

    targets = None
    if args:
        targets = args  # specific services

    import asyncio

    success = asyncio.run(sync_all_cookies(targets=targets, check_only=check_only))

    if success and not check_only:
        print("\n💡 建议: 现在可以运行采集脚本了")
        print("   python3 douyin_index_v9.py")
        print("   python3 competitor_keyword_v8.py")
        print("   ...")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
