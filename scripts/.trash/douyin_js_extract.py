#!/usr/bin/env python3
"""从JS变量提取数据"""
import asyncio
from playwright.async_api import async_playwright

async def extract_from_js():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        
        print(f"URL: {page.url}")
        
        # 尝试从window对象提取数据
        js_code = """
        () => {
            // 查找所有可能包含数据的全局变量
            const results = {};
            
            // 检查__NEXT_DATA__或其他data属性
            if (window.__NEXT_DATA__) {
                results.nextData = window.__NEXT_DATA__;
            }
            
            // 检查页面上的script标签中的数据
            const scripts = document.querySelectorAll('script');
            scripts.forEach((script, i) => {
                const text = script.textContent;
                if (text.includes('index') || text.includes('search')) {
                    // 提取JSON数据
                    const match = text.match(/\\{"[^}]+\\}/);
                    if (match) {
                        results[`script${i}`] = match[0].substring(0, 500);
                    }
                }
            });
            
            // 查找带有数据的DOM元素
            const dataDivs = document.querySelectorAll('[data-key], [data-value], [class*="data"]');
            results.dataDivs = Array.from(dataDivs).slice(0, 10).map(el => ({
                class: el.className,
                text: el.innerText?.substring(0, 100)
            }));
            
            return results;
        }
        """
        
        result = await page.evaluate(js_code)
        print("\n提取结果:")
        for key, value in result.items():
            print(f"\n{key}:")
            print(str(value)[:500])
        
        # 截图看看
        await page.screenshot(path='/tmp/douyin_current.png')
        print("\n截图: /tmp/douyin_current.png")
        
        await browser.close()

asyncio.run(extract_from_js())
