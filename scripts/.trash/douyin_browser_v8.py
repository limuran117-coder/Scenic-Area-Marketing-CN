#!/usr/bin/env python3
"""
抖音指数采集 - 提取data-gZFwhg元素
"""
import asyncio
import json
import re
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

async def extract_data(page):
    """从data元素提取指数"""
    try:
        await asyncio.sleep(2)
        
        # 查找data-gZFwhg类的元素
        js_code = """
        () => {
            const elements = document.querySelectorAll('[class*="data-gZFwhg"]');
            const data = [];
            elements.forEach(el => {
                const text = el.innerText;
                // 提取"平均值 XXXX"格式的数字
                const matches = text.match(/平均值[\\s:]*(\\d+)/g);
                if (matches) {
                    matches.forEach(m => {
                        const num = parseInt(m.replace(/[^0-9]/g, ''));
                        if (num >= 100 && num <= 500000) {
                            data.push(num);
                        }
                    });
                }
                // 也直接提取纯数字
                const directMatch = text.match(/^(\\d{4,6})$/m);
                if (directMatch) {
                    data.push(parseInt(directMatch[1]));
                }
            });
            return [...new Set(data)]; // 去重
        }
        """
        
        numbers = await page.evaluate(js_code)
        return numbers
        
    except Exception as e:
        print(f"提取出错: {e}")
        return []

async def search_and_collect(page, keyword):
    """搜索并采集数据"""
    try:
        # 找到输入框
        inputs = await page.query_selector_all('input')
        if inputs:
            await inputs[0].fill(keyword)
            await page.keyboard.press('Enter')
            await asyncio.sleep(3)
        
        # 提取数据
        numbers = await extract_data(page)
        return numbers
        
    except Exception as e:
        print(f"采集出错: {e}")
        return []

async def collect_all():
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        
        print(f"页面: {await page.title()}")
        print("=" * 60)
        
        for keyword in KEYWORDS:
            print(f"\n采集: {keyword}...", end=" ", flush=True)
            
            numbers = await search_and_collect(page, keyword)
            
            # 通常第一个是搜索指数，第二个是综合指数
            search_idx = numbers[0] if len(numbers) > 0 else None
            synthesis_idx = numbers[1] if len(numbers) > 1 else None
            
            print(f"搜索={search_idx}, 综合={synthesis_idx}")
            
            results.append({
                "keyword": keyword,
                "search": search_idx,
                "synthesis": synthesis_idx
            })
        
        await browser.close()
    
    return results

if __name__ == "__main__":
    print(f"开始采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = asyncio.run(collect_all())
    
    # 保存
    output = f"/tmp/crawl_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "data": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {output}")
    
    # 打印表格
    print("\n【抖音指数】")
    print("-" * 50)
    for r in results:
        s = str(r['search'] or 'N/A')
        sy = str(r['synthesis'] or 'N/A')
        print(f"| {r['keyword']:<16} | {s:>8} | {sy:>8} |")
