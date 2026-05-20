#!/usr/bin/env python3
"""小红书登录脚本 - 30秒超时自动保存"""
import asyncio
import json
from playwright.async_api import async_playwright

XHS_URL = "https://www.xiaohongshu.com/explore?channel_id=homefeed_recommend"
COOKIE_FILE = "/tmp/xiaohongshu_cookies.json"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            proxy={"server": "http://127.0.0.1:7897"}
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        print(f"正在打开 {XHS_URL} ...")
        print("请在30秒内完成登录...")
        
        try:
            await page.goto(XHS_URL, timeout=10000)
        except:
            pass
        
        # 等待30秒让用户登录
        await asyncio.sleep(30)
        
        # 保存Cookie
        cookies = await context.cookies()
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"Cookie已保存: {COOKIE_FILE}")
        print(f"共 {len(cookies)} 个Cookie")
        
        await browser.close()
        print("完成!")

asyncio.run(main())
