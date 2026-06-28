#!/opt/homebrew/bin/python3.12
"""
Day 23 探针 v2: 强制 hash 跳转 + 多阶段等待
"""
import asyncio, json
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:18800"
KEYWORD = "清明上河园"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()
        try:
            # 1. 先到根 URL，等 SPA 框架加载
            await page.goto("https://index.baidu.com/v2/main/index.html/", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(5000)
            t1_title = await page.title()
            t1_len = await page.evaluate("document.body.innerText.length")

            # 2. 通过 location.href 触发 hash 跳转
            await page.evaluate(f"window.location.href = 'https://index.baidu.com/v2/main/index.html#/trend/{KEYWORD}'")
            await page.wait_for_timeout(3000)

            # 3. 再手动等待 8s 让图表 + 数据 fetch 完
            await page.wait_for_timeout(8000)
            t2_title = await page.title()
            t2_len = await page.evaluate("document.body.innerText.length")
            t2_url = page.url

            # 4. dump
            text_dump = await page.evaluate("() => document.body.innerText")
            media = await page.evaluate("() => ({svg: document.querySelectorAll('svg').length, canvas: document.querySelectorAll('canvas').length, path_d: document.querySelectorAll('path[d]').length})")

            # 5. 抓包含"指数"的所有可见数字串
            import re
            nums = re.findall(r'[\d,]{2,}', text_dump or '')

            report = {
                "step1_root": {"title": t1_title, "body_text_len": t1_len},
                "step2_hash_jump": {"title": t2_title, "body_text_len": t2_len, "url": t2_url},
                "media_count": media,
                "body_text_first_1500": (text_dump or "")[:1500],
                "numbers_in_page_sample": nums[:40],
                "has_index_label": "搜索指数" in (text_dump or "") or "信息指数" in (text_dump or ""),
                "has_keyword": KEYWORD in (text_dump or ""),
            }
            print(json.dumps(report, ensure_ascii=False, indent=2))
        finally:
            await page.close()

asyncio.run(main())