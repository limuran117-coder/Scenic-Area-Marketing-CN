#!/usr/bin/env python3
"""调试特定关键词"""
import asyncio
from playwright.async_api import async_playwright

async def debug_keywords():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        
        # 测试这两个关键词
        test_keywords = ["万岁山武侠城", "清明上河园"]
        
        for keyword in test_keywords:
            print(f"\n测试: {keyword}")
            
            # 输入
            inputs = await page.query_selector_all('input')
            if inputs:
                await inputs[0].click()
                await asyncio.sleep(0.3)
                await page.keyboard.press('Meta+a')
                await asyncio.sleep(0.2)
                await page.keyboard.press('Backspace')
                await asyncio.sleep(0.2)
                await inputs[0].type(keyword, delay=50)
                await asyncio.sleep(0.5)
                await page.keyboard.press('Enter')
                
                # 等待
                await asyncio.sleep(5)
                
                # 检查URL
                print(f"  URL: {page.url}")
                
                # 获取数据
                js_code = """
                () => {
                    const elements = document.querySelectorAll('[class*="data-gZFwhg"]');
                    const data = [];
                    elements.forEach(el => {
                        data.push(el.innerText.substring(0, 200));
                    });
                    return data;
                }
                """
                elements = await page.evaluate(js_code)
                print(f"  找到元素: {len(elements)}")
                for j, el in enumerate(elements[:3]):
                    print(f"    元素{j}: {el}")
        
        await browser.close()

asyncio.run(debug_keywords())
