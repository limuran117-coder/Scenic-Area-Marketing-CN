#!/usr/bin/env python3
"""小红书测试 - 使用系统代理"""
import asyncio
import json
from playwright.async_api import async_playwright

XHS_URL = "https://www.xiaohongshu.com/explore?channel_id=homefeed_recommend"
COOKIE_FILE = "/tmp/xiaohongshu_cookies.json"

async def main():
    async with async_playwright() as p:
        # 使用代理
        browser = await p.chromium.launch(
            headless=True,
            proxy={
                "server": "http://127.0.0.1:7897",
                "bypass": ".local,localhost"
            }
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 加载Cookie
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        print(f"正在访问 {XHS_URL} ...")
        await page.goto(XHS_URL, timeout=60000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        text = await page.inner_text('body')
        print("页面内容前500字:")
        print(text[:500])
        
        await browser.close()

asyncio.run(main())
