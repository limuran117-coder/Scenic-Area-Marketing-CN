#!/usr/bin/env python3
import asyncio
import json
import re
from playwright.async_api import async_playwright

SPOTS = ["建业电影小镇", "万岁山武侠城", "清明上河园", "只有河南戏剧幻城", "郑州方特欢乐世界", "郑州银基动物王国"]

results = {}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
        context = browser.contexts[0]
        
        # Find the lingxi page
        target_page = None
        for page in context.pages:
            if 'xiaohongshu.com/idea/trend' in page.url:
                target_page = page
                break
        
        if not target_page:
            print("Lingxi page not found!")
            return
        
        for spot in SPOTS:
            try:
                # Click the search input
                placeholder = target_page.locator('text=请输入想查询的内容，点击下拉框关键词即可查询')
                await placeholder.click()
                await asyncio.sleep(0.5)
                
                # Clear and type
                await target_page.keyboard.press('Control+a')
                await target_page.keyboard.press('Backspace')
                await asyncio.sleep(0.3)
                await target_page.keyboard.type(spot)
                await asyncio.sleep(2)
                await target_page.keyboard.press('ArrowDown')
                await asyncio.sleep(0.3)
                await target_page.keyboard.press('Enter')
                await asyncio.sleep(5)
                
                # Extract data
                text = await target_page.evaluate('document.body.innerText')
                
                # Parse the data
                search_match = re.search(r'搜索总量(\S+)', text)
                环比_match = re.search(r'环比([+-]?\d+\.?\d*%)', text)
                同比_match = re.search(r'同比([+-]?\d+\.?\d*%)', text)
                
                # Extract TOP 10 keywords - look for pattern like "1  建业电影小镇  8424"
                keywords = re.findall(r'\d+\s+([^\s]+)\s+(\d+)', text)
                
                results[spot] = {
                    "搜索总量": search_match.group(1) if search_match else "—",
                    "环比": 环比_match.group(1) if 环比_match else "—",
                    "同比": 同比_match.group(1) if 同比_match else "—",
                    "TOP10": keywords[:10]
                }
                print(f"Got data for {spot}: {results[spot]}")
                
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Error for {spot}: {e}")
                results[spot] = {"error": str(e)}
        
        # Save results
        with open('/tmp/xhs_competitors.json', 'w') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("Saved to /tmp/xhs_competitors.json")

if __name__ == "__main__":
    asyncio.run(main())