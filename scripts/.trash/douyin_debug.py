#!/usr/bin/env python3
"""
调试脚本 - 查看抖音页面实际内容
"""
import asyncio
from playwright.async_api import async_playwright

async def debug_page():
    async with async_playwright() as p:
        print("连接Chrome...")
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        else:
            page = await browser.new_page()
        
        print(f"页面标题: {await page.title()}")
        print(f"页面URL: {page.url}")
        
        # 截图
        await page.screenshot(path='/tmp/douyin_page.png')
        print("截图已保存到: /tmp/douyin_page.png")
        
        # 获取页面文本
        text = await page.inner_text('body')
        print("\n页面文本内容 (前2000字符):")
        print("-" * 40)
        print(text[:2000] if len(text) > 2000 else text)
        print("-" * 40)
        
        # 查找所有输入框
        inputs = await page.query_selector_all('input')
        print(f"\n找到 {len(inputs)} 个输入框")
        
        await browser.close()

asyncio.run(debug_page())
