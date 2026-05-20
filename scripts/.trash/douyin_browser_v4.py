#!/usr/bin/env python3
"""
抖音关键词指数采集 - 简化版
使用Chrome CDP连接，直接URL导航
"""
import asyncio
import json
import re
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

def extract_numbers_from_page(content):
    """从页面HTML中提取指数数据"""
    # 查找所有数字
    numbers = re.findall(r'([\d,]+)', content)
    
    valid_numbers = []
    for num_str in numbers:
        num = int(num_str.replace(',', ''))
        # 抖音指数范围大约是500 - 500000
        if 500 <= num <= 500000:
            valid_numbers.append(num)
    
    return valid_numbers

async def collect_data():
    """采集所有关键词数据"""
    results = {}
    all_data = []
    
    async with async_playwright() as p:
        # 连接到Chrome CDP
        print("正在连接Chrome...")
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        # 获取当前页面
        if browser.contexts:
            context = browser.contexts[0]
            if context.pages:
                page = context.pages[0]
                await page.bring_to_front()
                print(f"当前页面: {await page.title()}")
            else:
                page = await context.new_page()
        else:
            page = await browser.new_page()
        
        for keyword in KEYWORDS:
            print(f"\n采集: {keyword}...")
            
            # 方法：直接导航到搜索URL
            keyword_encoded = keyword  # 中文应该被URL编码
            
            # 在搜索框中输入关键词
            try:
                # 查找搜索框
                search_input = await page.query_selector('input')
                if search_input:
                    await search_input.fill(keyword)
                    await asyncio.sleep(2)
                    
                    # 点击搜索按钮或按回车
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(3)
                    
                    # 获取页面内容
                    content = await page.content()
                    numbers = extract_numbers_from_page(content)
                    
                    print(f"  找到数字: {numbers[:6]}")
                    
                    if len(numbers) >= 2:
                        search_idx = numbers[0]
                        synthesis_idx = numbers[1]
                    elif len(numbers) == 1:
                        search_idx = numbers[0]
                        synthesis_idx = None
                    else:
                        search_idx = None
                        synthesis_idx = None
                    
                    results[keyword] = {
                        "search": search_idx,
                        "synthesis": synthesis_idx
                    }
                    all_data.append({
                        "keyword": keyword,
                        "search": search_idx,
                        "synthesis": synthesis_idx
                    })
                    print(f"  搜索={search_idx}, 综合={synthesis_idx}")
                else:
                    print(f"  未找到搜索框")
                    results[keyword] = {"search": None, "synthesis": None}
            except Exception as e:
                print(f"  出错: {e}")
                results[keyword] = {"search": None, "synthesis": None}
        
        await browser.close()
    
    return results, all_data

if __name__ == "__main__":
    print(f"开始采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results, all_data = asyncio.run(collect_data())
    
    # 保存结果
    output_file = f"/tmp/crawl_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "data": all_data,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"采集完成，结果已保存到: {output_file}")
