#!/usr/bin/env python3
"""
抖音关键词指数采集 - 完整版
采集8个景区的搜索指数和综合指数
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

async def get_index_from_page(page):
    """获取搜索指数和综合指数"""
    try:
        await asyncio.sleep(2)
        
        # 获取页面完整文本
        text = await page.inner_text('body')
        
        # 打印前3000字符看看结构
        print("页面内容预览:")
        print(text[:3000])
        print("...")
        
        return {"search": None, "synthesis": None}
        
    except Exception as e:
        print(f"获取数据出错: {e}")
        return {"search": None, "synthesis": None}

async def search_keyword(page, keyword):
    """搜索关键词"""
    try:
        # 找到搜索框并输入
        inputs = await page.query_selector_all('input')
        print(f"找到 {len(inputs)} 个输入框")
        
        for i, inp in enumerate(inputs):
            placeholder = await inp.get_attribute('placeholder')
            print(f"  输入框{i}: placeholder={placeholder}")
        
        # 通常第一个输入框是关键词搜索
        if inputs:
            search_input = inputs[0]
            await search_input.fill(keyword)
            await asyncio.sleep(1)
            await page.keyboard.press('Enter')
            await asyncio.sleep(3)
            print(f"已搜索: {keyword}")
            
    except Exception as e:
        print(f"搜索出错: {e}")

async def collect_data():
    results = {}
    
    async with async_playwright() as p:
        print("连接Chrome...")
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        else:
            page = await browser.new_page()
        
        print(f"页面: {await page.title()}")
        print("=" * 60)
        
        # 先获取当前页面的数据
        print("\n获取当前页面数据...")
        data = await get_index_from_page(page)
        print(f"\n当前关键词数据: {data}")
        
        await browser.close()
    
    return results

asyncio.run(collect_data())
