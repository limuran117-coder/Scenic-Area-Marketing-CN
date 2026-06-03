#!/usr/bin/env python3
"""
抖音指数采集 - 修复万单位
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

def parse_chinese_number(text):
    """解析中文数字，如'8.2万' -> 82000"""
    text = text.strip()
    if '万' in text:
        num = float(text.replace('万', ''))
        return int(num * 10000)
    elif '万' in text:
        # 处理整数的万
        num = int(text.replace('万', ''))
        return num * 10000
    else:
        try:
            return int(text)
        except:
            return None

async def extract_data(page):
    """提取数据"""
    try:
        js_code = """
        () => {
            const elements = document.querySelectorAll('[class*="data-gZFwhg"]');
            const data = [];
            elements.forEach(el => {
                const text = el.innerText;
                data.push(text);
            });
            return data;
        }
        """
        texts = await page.evaluate(js_code)
        
        numbers = []
        for text in texts:
            # 匹配 "平均值 X万" 或 "平均值 X.X万" 格式
            matches = re.findall(r'平均值\s*([\d.]+万|\d+)', text)
            for m in matches:
                num = parse_chinese_number(m)
                if num and 100 <= num <= 5000000:
                    numbers.append(num)
        
        # 去重并排序
        return sorted(set(numbers), reverse=True)
        
    except Exception as e:
        print(f"提取出错: {e}")
        return []

async def wait_for_data(page, timeout=10):
    """等待数据加载"""
    for _ in range(timeout):
        numbers = await extract_data(page)
        if numbers:
            return numbers
        await asyncio.sleep(1)
    return []

async def search_keyword(page, keyword):
    """搜索关键词"""
    try:
        inputs = await page.query_selector_all('input')
        if inputs:
            inp = inputs[0]
            await inp.click()
            await asyncio.sleep(0.3)
            await page.keyboard.press('Meta+a')
            await asyncio.sleep(0.2)
            await page.keyboard.press('Backspace')
            await asyncio.sleep(0.2)
            await inp.type(keyword, delay=50)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            await asyncio.sleep(4)
    except Exception as e:
        print(f"搜索出错: {e}")

async def collect_all():
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        
        print(f"页面: {await page.title()}")
        print("=" * 60)
        
        for i, keyword in enumerate(KEYWORDS):
            print(f"\n[{i+1}/{len(KEYWORDS)}] {keyword}...", end=" ", flush=True)
            
            await search_keyword(page, keyword)
            numbers = await wait_for_data(page, timeout=8)
            
            search_idx = numbers[0] if len(numbers) > 0 else None
            synthesis_idx = numbers[1] if len(numbers) > 1 else None
            
            # 格式化输出
            s = f"{search_idx:,}" if search_idx else "N/A"
            sy = f"{synthesis_idx:,}" if synthesis_idx else "N/A"
            print(f"搜索={s}, 综合={sy}")
            
            results.append({
                "keyword": keyword,
                "search_index": search_idx,
                "synthesis_index": synthesis_idx
            })
        
        await browser.close()
    
    return results

if __name__ == "__main__":
    print(f"开始采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = asyncio.run(collect_all())
    
    output = f"/tmp/crawl_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "Chrome CDP",
            "data": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {output}")
    
    print("\n【抖音指数汇总】")
    print("-" * 55)
    print("| {:<16} | {:>12} | {:>12} |".format("景区", "搜索指数", "综合指数"))
    print("-" * 55)
    for r in results:
        s = f"{r['search_index']:,}" if r['search_index'] else "N/A"
        sy = f"{r['synthesis_index']:,}" if r['synthesis_index'] else "N/A"
        print(f"| {r['keyword']:<16} | {s:>12} | {sy:>12} |")
    print("-" * 55)
