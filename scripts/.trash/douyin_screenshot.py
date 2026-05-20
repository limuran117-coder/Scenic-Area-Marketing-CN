#!/usr/bin/env python3
"""截图并分析页面结构"""
import asyncio
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        
        print(f"URL: {page.url}")
        
        # 截图
        await page.screenshot(path='/tmp/douyin_analysis.png', full_page=False)
        print("截图: /tmp/douyin_analysis.png")
        
        # 查找所有canvas
        canvases = await page.query_selector_all('canvas')
        print(f"\n找到 {len(canvases)} 个canvas元素")
        
        # 查找包含数字的div
        divs = await page.query_selector_all('div')
        numbers_found = []
        for div in divs[:200]:  # 只检查前200个
            try:
                text = await div.inner_text()
                import re
                if re.match(r'^\d{4,6}$', text.strip()):
                    numbers_found.append(text.strip())
            except:
                pass
        
        print(f"\n找到纯数字div: {numbers_found}")
        
        # 查找svg
        svgs = await page.query_selector_all('svg')
        print(f"\n找到 {len(svgs)} 个svg元素")
        
        await browser.close()

asyncio.run(analyze())
