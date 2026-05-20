#!/usr/bin/env python3
"""
抖音关键词指数采集 - 使用JS评估提取数据
通过已有Chrome浏览器采集数据
"""
import asyncio
import json
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

async def extract_data_via_js(page):
    """通过JS提取页面数据"""
    try:
        # 等待数据加载
        await asyncio.sleep(2)
        
        # 尝试多种方式获取数据
        
        # 方法1: 获取所有文本节点中的数字
        js_code = """
        () => {
            // 尝试从页面元素中提取数据
            const result = { search: null, synthesis: null };
            
            // 查找包含"搜索指数"或"综合指数"的元素
            const allText = document.body.innerText;
            
            // 尝试匹配类似"85,759"或"85759"的数字模式
            const numberMatches = allText.match(/\\d{1,3}(,\\d{3})+|^\\d{4,6}/gm);
            
            if (numberMatches && numberMatches.length > 0) {
                const numbers = numberMatches.map(n => parseInt(n.replace(/,/g, '')));
                // 过滤有效范围
                const valid = numbers.filter(n => n >= 1000 && n <= 300000);
                if (valid.length >= 2) {
                    result.search = valid[0];
                    result.synthesis = valid[1];
                } else if (valid.length === 1) {
                    result.search = valid[0];
                }
            }
            
            // 尝试查找特定class或id的元素
            const indicators = document.querySelectorAll('[class*="index"], [class*="indicator"]');
            indicators.forEach(el => {
                const text = el.innerText;
                const match = text.match(/\\d+/);
                if (match) {
                    const num = parseInt(match[0]);
                    if (num >= 1000 && num <= 300000) {
                        if (!result.search) result.search = num;
                        else if (!result.synthesis) result.synthesis = num;
                    }
                }
            });
            
            return result;
        }
        """
        
        result = await page.evaluate(js_code)
        return result
        
    except Exception as e:
        print(f"JS提取出错: {e}")
        return {"search": None, "synthesis": None}

async def search_and_extract(page, keyword):
    """搜索关键词并提取数据"""
    try:
        # 清除搜索框并输入新关键词
        search_input = await page.query_selector('input')
        if search_input:
            await search_input.click()
            await asyncio.sleep(0.5)
            
            # 全选并删除
            await page.keyboard.press('Meta+a')
            await page.keyboard.press('Backspace')
            await asyncio.sleep(0.5)
            
            # 输入新关键词
            await search_input.type(keyword, delay=100)
            await asyncio.sleep(1)
            
            # 按回车搜索
            await page.keyboard.press('Enter')
            await asyncio.sleep(3)
            
            # 提取数据
            data = await extract_data_via_js(page)
            return data
        else:
            print("未找到搜索框")
            return {"search": None, "synthesis": None}
            
    except Exception as e:
        print(f"搜索出错: {e}")
        return {"search": None, "synthesis": None}

async def collect_data():
    """采集所有关键词数据"""
    results = {}
    all_data = []
    
    async with async_playwright() as p:
        print("正在连接Chrome...")
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        # 获取当前页面
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            await page.bring_to_front()
        else:
            page = await browser.new_page()
            await page.goto('https://creator.douyin.com/creator-micro/creator-count/arithmetic-index/analysis')
            await asyncio.sleep(5)
        
        print(f"当前页面: {await page.title()}")
        print("=" * 60)
        
        for keyword in KEYWORDS:
            print(f"\n采集: {keyword}...", end=" ", flush=True)
            
            data = await search_and_extract(page, keyword)
            results[keyword] = data
            all_data.append({
                "keyword": keyword,
                "search": data.get("search"),
                "synthesis": data.get("synthesis")
            })
            
            print(f"搜索={data.get('search')}, 综合={data.get('synthesis')}")
        
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
    
    # 打印摘要表格
    print("\n【抖音指数汇总】")
    print("-" * 40)
    for item in all_data:
        s = item.get('search', 'N/A')
        sy = item.get('synthesis', 'N/A')
        print(f"| {item['keyword']:<16} | {str(s):>8} | {str(sy):>8} |")
