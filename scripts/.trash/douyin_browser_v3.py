#!/usr/bin/env python3
"""
抖音关键词指数采集 - 使用Chrome CDP连接
通过已有Chrome浏览器采集数据，保留登录状态
"""
import asyncio
import json
import re
import sys
from datetime import datetime
from playwright.async_api import async_playwright

# 8个景区关键词
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

async def extract_index_data(page):
    """从页面提取搜索指数和综合指数"""
    data = {"search": None, "synthesis": None}
    
    try:
        # 等待数据加载
        await asyncio.sleep(2)
        
        # 获取页面文本内容
        content = await page.content()
        
        # 提取数字 - 查找类似"85,759"或"85759"的数字
        # 搜索指数通常在页面上方
        numbers = re.findall(r'([\d,]+)', content)
        
        # 过滤出合理的指数值（5位或6位数字）
        valid_numbers = []
        for num_str in numbers:
            num = int(num_str.replace(',', ''))
            if 500 <= num <= 500000:
                valid_numbers.append(num)
        
        if len(valid_numbers) >= 2:
            # 假设第一个是搜索指数，第二个是综合指数
            data["search"] = valid_numbers[0]
            data["synthesis"] = valid_numbers[1]
        elif len(valid_numbers) == 1:
            data["search"] = valid_numbers[0]
            
    except Exception as e:
        print(f"提取数据出错: {e}")
    
    return data

async def search_keyword(page, keyword):
    """搜索关键词"""
    try:
        # 查找搜索框并输入
        search_box = await page.query_selector('input[placeholder*="搜索"]')
        if not search_box:
            search_box = await page.query_selector('input[type="text"]')
        
        if search_box:
            await search_box.fill(keyword)
            await page.keyboard.press('Enter')
            await asyncio.sleep(3)
            print(f"  已搜索: {keyword}")
        else:
            print(f"  未找到搜索框")
            
    except Exception as e:
        print(f"  搜索出错: {e}")

async def collect_data():
    """采集所有关键词数据"""
    results = {}
    
    async with async_playwright() as p:
        # 连接到Chrome CDP
        print("正在连接Chrome...")
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        # 获取当前页面
        context = browser.contexts[0] if browser.contexts else None
        if context and context.pages:
            page = context.pages[0]
            await page.bring_to_front()
        else:
            page = await browser.new_page()
            await page.goto('https://creator.douyin.com/creator-micro/creator-count/arithmetic-index/analysis')
            await asyncio.sleep(3)
        
        print(f"当前页面: {await page.title()}")
        print("=" * 50)
        
        for keyword in KEYWORDS:
            print(f"\n采集: {keyword}")
            
            # 搜索关键词
            await search_keyword(page, keyword)
            
            # 提取数据
            data = await extract_index_data(page)
            results[keyword] = data
            
            print(f"  搜索指数: {data.get('search', 'N/A')}")
            print(f"  综合指数: {data.get('synthesis', 'N/A')}")
        
        await browser.close()
    
    return results

if __name__ == "__main__":
    print(f"开始采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = asyncio.run(collect_data())
    
    # 保存结果
    output_file = f"/tmp/crawl_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print(f"采集完成，结果已保存到: {output_file}")
    print("\n结果摘要:")
    for keyword, data in results.items():
        print(f"  {keyword}: 搜索={data.get('search', 'N/A')}, 综合={data.get('synthesis', 'N/A')}")
