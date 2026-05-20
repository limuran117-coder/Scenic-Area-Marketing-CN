#!/usr/bin/env python3
"""
抖音关键词指数采集 - 点击正确标签
"""
import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

KEYWORDS = [
    "建业电影小镇",
    "万岁山武侠城", 
    "清明上河园",
    "只有河南戏剧幻城",
    "郑州方特欢乐世界",
    "郑州海昌海洋公园",
    "郑州银基动物王国",
    "只有红楼梦戏剧幻城"
]

async def click_tab_and_get_data(page, tab_name):
    """点击标签并获取数据"""
    try:
        # 查找包含文字的元素
        tabs = await page.query_selector_all('span')
        for tab in tabs:
            text = await tab.inner_text()
            if tab_name in text:
                await tab.click()
                print(f"点击了标签: {tab_name}")
                await asyncio.sleep(3)
                break
        
        # 获取页面文本
        text = await page.inner_text('body')
        return text
        
    except Exception as e:
        print(f"点击标签出错: {e}")
        return ""

async def extract_numbers(text):
    """从文本中提取抖音指数"""
    import re
    
    # 抖音指数通常是4-6位数字，在关键词附近
    # 搜索模式：查找"搜索指数"后面的数字或紧跟在大数字后面的
    lines = text.split('\n')
    
    numbers = []
    for i, line in enumerate(lines):
        line = line.strip()
        # 查找纯数字行（可能是指数）
        if re.match(r'^\d{4,6}$', line):
            numbers.append(int(line))
    
    # 返回最大的两个（通常是搜索和综合指数）
    numbers = sorted(set(numbers), reverse=True)[:2]
    return numbers

async def collect_all():
    results = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        else:
            page = await browser.new_page()
        
        print(f"页面: {await page.title()}")
        print("=" * 60)
        
        for keyword in KEYWORDS:
            print(f"\n采集: {keyword}")
            
            # 输入关键词
            inputs = await page.query_selector_all('input')
            if inputs:
                await inputs[0].fill(keyword)
                await page.keyboard.press('Enter')
                await asyncio.sleep(3)
            
            # 点击"关键词指数"标签
            text = await click_tab_and_get_data(page, "关键词指数")
            
            # 提取数字
            nums = await extract_numbers(text)
            print(f"提取到数字: {nums}")
            
            if len(nums) >= 2:
                results[keyword] = {"search": nums[0], "synthesis": nums[1]}
            elif len(nums) == 1:
                results[keyword] = {"search": nums[0], "synthesis": None}
            else:
                results[keyword] = {"search": None, "synthesis": None}
            
            print(f"结果: 搜索={results[keyword]['search']}, 综合={results[keyword]['synthesis']}")
        
        await browser.close()
    
    return results

if __name__ == "__main__":
    print(f"开始采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = asyncio.run(collect_all())
    
    # 保存
    output = f"/tmp/crawl_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output, 'w') as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": results}, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {output}")
