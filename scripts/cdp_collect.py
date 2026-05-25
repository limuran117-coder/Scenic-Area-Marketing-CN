#!/opt/homebrew/bin/python3.12
"""
CDP采集脚本 - 连接browser-use Chrome的3个Tab采集数据
窗口常开，不走launch，不产生daemon

Tab对应：
  Tab1: 抖音订阅页（综合指数）
  Tab2: 抖音关键词搜索页（搜索指数）
  Tab3: 小红书

使用方法：
  python3 cdp_collect.py
"""

import asyncio
import json
import time
import re
import sys
import os

# 专属Chrome（用户登录后保持常开，不关闭）
# 端口: 9222
# Tab1: 抖音订阅页 | Tab2: 抖音关键词页 | Tab3: 小红书
CDP_ENDPOINT = "http://127.0.0.1:9222"

SCENIC_SPOTS = [
    "建业电影小镇",
    "万岁山武侠城",
    "清明上河园",
    "只有河南戏剧幻城",
    "郑州方特欢乐世界",
    "郑州海昌海洋公园",
    "郑州银基动物王国",
    "只有红楼梦戏剧幻城"
]

def parse_number(text):
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def parse_scenic_block(block_text):
    """解析单个景区区块（按景区名分割后独立解析）"""
    data = {"name": "", "search": 0, "synth": 0, "search_trend": "", "synth_trend": ""}
    lines = block_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 日环比（判断是搜索还是综合）
        if '日环比' in line and i + 1 < len(lines):
            trend = lines[i + 1].strip()
            if '%' in trend:
                if data["search"] > 0 and data["synth"] == 0:
                    data["search_trend"] = trend
                elif data["search"] > 0 and data["synth"] > 0:
                    data["synth_trend"] = trend
        
        # 搜索指数（跳过"有异动"）
        if line == '搜索指数':
            for k in range(i + 1, min(i + 4, len(lines))):
                val = lines[k].strip()
                if '有异动' in val or not val:
                    continue
                n = parse_number(val)
                if n > 0:
                    data["search"] = n
                    break
        
        # 综合指数（跳过"有异动"）
        if line == '综合指数':
            for k in range(i + 1, min(i + 4, len(lines))):
                val = lines[k].strip()
                if '有异动' in val or not val:
                    continue
                n = parse_number(val)
                if n > 0:
                    data["synth"] = n
                    break
    
    return data

def parse_full_page(text):
    """将页面按景区名分割，逐块解析，避免数据串位"""
    results = {}
    pattern = '|'.join(SCENIC_SPOTS)
    parts = re.split(f'({pattern})', text)
    
    i = 1
    while i < len(parts) - 1:
        name = parts[i].strip()
        if name in SCENIC_SPOTS:
            # 找到下一个景区名的位置
            next_pos = float('inf')
            for j in range(i + 2, len(parts), 2):
                if parts[j].strip() in SCENIC_SPOTS:
                    next_pos = j
                    break
            block = ''.join(parts[i:next_pos]) if next_pos < len(parts) else ''.join(parts[i:])
            data = parse_scenic_block(block)
            data["name"] = name
            results[name] = data
        i += 2
    
    return results

async def crawl_douyin():
    """采集抖音数据"""
    from playwright.async_api import async_playwright
    
    print("\n" + "=" * 50)
    print("CDP采集 - 抖音指数")
    print("=" * 50)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print(f"✅ 已连接 Chrome")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return None
        
        context = browser.contexts[0]
        
        # 找抖音订阅Tab
        sub_page = None
        for page in context.pages:
            if 'my-subscript' in page.url:
                sub_page = page
                break
        
        if not sub_page:
            print("❌ 未找到抖音订阅Tab")
            return None
        
        print("  刷新订阅页...")
        try:
            await sub_page.goto(sub_page.url, timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(5)
            text = await sub_page.evaluate("document.body ? document.body.innerText : ''")
        except Exception as e:
            print(f"  刷新失败: {e}")
            return None
        
        # 解析数据
        results = parse_full_page(text)
        
        today = time.strftime("%Y-%m-%d")
        output = {
            "date": today,
            "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "competitors": [],
            "data_url": "https://creator.douyin.com/creator-micro/creator-count/my-subscript"
        }
        
        print("\n  解析结果：")
        for name in SCENIC_SPOTS:
            d = results.get(name, {})
            if d.get("search") > 0 or d.get("synth") > 0:
                output["competitors"].append(d)
                print(f"    ✅ {name}: 搜索={d['search']}, 综合={d['synth']}")
            else:
                print(f"    ⚠️  {name}: 未找到")
        
        return output

async def crawl_xiaohongshu():
    """采集小红书数据（刷新页面，返回状态）"""
    from playwright.async_api import async_playwright
    
    print("\n" + "=" * 50)
    print("CDP采集 - 小红书")
    print("=" * 50)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
        except Exception as e:
            print(f"  连接失败: {e}")
            return None
        
        context = browser.contexts[0]
        
        xhs_page = None
        for page in context.pages:
            if 'xiaohongshu' in page.url.lower():
                xhs_page = page
                print(f"  找到小红书Tab: {page.url[:60]}")
                break
        
        if not xhs_page:
            print("  ❌ 未找到小红书Tab")
            return None
        
        print("  刷新小红书...")
        try:
            await xhs_page.goto("https://www.xiaohongshu.com/explore", timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(3)
            print("  ✅ 小红书Tab已刷新")
        except Exception as e:
            print(f"  ⚠️ 刷新失败: {e}")
        
        return {"status": "ok"}

async def main():
    # 采集抖音
    result = await crawl_douyin()
    
    if result and result["competitors"]:
        with open("/tmp/crawl_data.json", 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 抖音数据已保存: /tmp/crawl_data.json")
        print(f"   有效数据: {len(result['competitors'])}/8 个景区")
    
    # 采集小红书
    xhs = await crawl_xiaohongshu()
    if xhs:
        with open("/tmp/crawl_xhs_status.json", 'w') as f:
            json.dump(xhs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
