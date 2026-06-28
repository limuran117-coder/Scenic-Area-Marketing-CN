#!/opt/homebrew/bin/python3.12
"""
百度指数爬虫 (CDP) → JSON → adapter-baidu.py

⚠️ Day 21 (2026-06-20) 最小骨架版本:
  - 复用 cdp_collect.py 的 CDP 连接模式 (18800)
  - 已知限制: 仅清明上河园有公开数据 (Day 6 实测, 12.5% 覆盖率)
  - Day 21 目标: 抓 1 个关键词 (清明上河园), 验证端到端链路
  - 后续: 评估是否投入扩展到 8 景区

数据流:
  CDP Chrome (已登录李思洋912) 
    → playwright connect_over_cdp 
    → navigate https://index.baidu.com/v2/main/index.html#/trend/清明上河园
    → wait + extract 页面数据
    → JSON 输出到 /tmp/baidu_index_{date}.json
    → adapter-baidu.py --data /tmp/baidu_index_{date}.json

Day 6 实测覆盖率:
  ✅ 清明上河园        → search_index=563, info_index=931584
  ❌ 建业电影小镇      → 搜索量低于收录阈值
  ❌ 只有河南/万岁山    → 需购买创建新词权限
"""

import argparse
import asyncio
import json
import sys
import os
from datetime import datetime

# ── 常量 ──────────────────────────────────────────────────
CDP_URL = "http://127.0.0.1:18800"

BAIDU_INDEX_BASE = "https://index.baidu.com/v2/main/index.html#/trend/"

# Day 21 验证集: 只抓 1 个有数据的关键词 (清明上河园)
DAY21_KEYWORD = "清明上河园"


async def crawl_one_keyword(keyword: str, output_path: str):
    """
    通过已登录 CDP Chrome 抓 1 个关键词的百度指数
    
    ⚠️ Day 21 stub: 用 playwright connect 但只 navigate + 截图,
       实际 DOM 解析留作 Day 22 工作 (需先验证 URL pattern 是否稳定)
    """
    from playwright.async_api import async_playwright
    
    url = BAIDU_INDEX_BASE + keyword
    print(f"📡 navigate: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # 等百度指数图表渲染 (实测需 3-5s)
            await page.wait_for_timeout(5000)
            
            # Day 21 最小验证: 截图 + title 抓取
            title = await page.title()
            print(f"  📄 title: {title}")
            
            screenshot_path = output_path.replace(".json", ".png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"  📸 screenshot: {screenshot_path}")
            
            # 桩数据: 留给 Day 22 实现 DOM 解析
            payload = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "crawled_at": datetime.now().isoformat(),
                "source": "baidu-index",
                "status": "STUB",
                "note": "Day 21: 验证 CDP 连接 + URL pattern; DOM 解析待 Day 22",
                "keywords": {
                    keyword: {
                        "search_index": None,
                        "info_index": None,
                        "search_trend": None,
                        "info_trend": None,
                        "region_top3": [],
                        "audience": {},
                        "_meta": {
                            "url": url,
                            "title": title,
                            "screenshot": screenshot_path,
                        }
                    }
                }
            }
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 JSON 写出: {output_path}")
            print(f"  ⚠️ search_index=None (待 Day 22 DOM 解析)")
            return payload
            
        finally:
            await page.close()


def main():
    parser = argparse.ArgumentParser(
        description="百度指数爬虫 (CDP) → JSON (Day 21 最小骨架)",
        epilog="前置条件: CDP Chrome 已运行在端口 18800 + 已登录百度指数账号"
    )
    parser.add_argument(
        "--keyword", default=DAY21_KEYWORD,
        help=f"关键词 (默认: {DAY21_KEYWORD}, 唯一确认有数据的景区)"
    )
    parser.add_argument(
        "--output", default=None,
        help="JSON 输出路径 (默认: /tmp/baidu_index_<date>.json)"
    )
    args = parser.parse_args()
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_path = args.output or f"/tmp/baidu_index_{date_str}.json"
    
    print("=" * 60)
    print(" crawl_baidu.py — 百度指数爬虫 (Day 21 骨架)")
    print("=" * 60)
    print(f"关键词: {args.keyword}")
    print(f"输出: {output_path}")
    print(f"CDP: {CDP_URL}")
    print()
    
    try:
        payload = asyncio.run(crawl_one_keyword(args.keyword, output_path))
        print()
        print("=" * 60)
        print("✅ Day 21 完成: CDP 连接 + URL pattern + 截图 三件套验证")
        print("=" * 60)
        print()
        print("Day 22 待办:")
        print("  - DOM 解析: 提取 search_index / info_index 数值")
        print("  - 趋势图 SVG/Canvas 数据读取 (方式B) 或 XHR 拦截 (方式C)")
        print("  - 决定是否扩展到其他有数据的关键词")
        print()
        print("⚠️ 注意: 12.5% 覆盖率 (1/8 景区), 需要评估投入产出比")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()