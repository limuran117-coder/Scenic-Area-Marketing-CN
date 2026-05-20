#!/usr/bin/env python3
"""
抖音数据采集脚本 - 连接用户Chrome
使用CDP连接到用户已有的Chrome浏览器
"""

import json
import asyncio
from playwright.async_api import async_playwright

# 景区关键词列表
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

def parse_numbers_from_text(text, spot_name):
    """从关键词页面文本中提取数据"""
    lines = text.split('\n')
    data = {"name": spot_name, "search": None, "synth": None, "search_trend": None, "synth_trend": None}
    
    for i, line in enumerate(lines):
        line = line.strip()
        # 搜索指数
        if '搜索指数' in line:
            # 下一行可能是数值
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip().replace('%', '').replace('+', '')
                if next_line.replace('.', '').replace('-', '').isdigit() or (next_line.replace(',', '').replace('.', '').replace('-', '').isdigit()):
                    try:
                        val = float(next_line.replace(',', ''))
                        if 0 < val < 1000000:
                            if data["search"] is None:
                                data["search"] = int(val)
                            else:
                                data["search_trend"] = next_line
                            break
                    except:
                        pass
        # 综合指数
        if '综合指数' in line:
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip().replace('%', '').replace('+', '')
                if next_line.replace('.', '').replace('-', '').isdigit() or (next_line.replace(',', '').replace('.', '').replace('-', '').isdigit()):
                    try:
                        val = float(next_line.replace(',', ''))
                        if 0 < val < 1000000:
                            if data["synth"] is None:
                                data["synth"] = int(val)
                            else:
                                data["synth_trend"] = next_line
                            break
                    except:
                        pass
    
    return data

async def main():
    print("=" * 60)
    print("抖音数据采集 - 连接用户Chrome")
    print("=" * 60)
    
    async with async_playwright() as p:
        # 连接到用户的Chrome
        print("\n[1] 连接到Chrome浏览器...")
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("   ✅ 已连接")
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            return
        
        # 创建新页面
        page = await browser.new_page()
        
        # 采集数据
        results = []
        
        print("\n[2] 采集数据...")
        for i, spot in enumerate(SCENIC_SPOTS, 1):
            print(f"\n   [{i}/8] 搜索: {spot}")
            
            try:
                # 访问关键词搜索页
                search_url = f"https://creator.douyin.com/creator-micro/creator-count/arithmetic-index?keyword={spot}"
                await page.goto(search_url, timeout=60000)
                await page.wait_for_load_state("networkidle", timeout=30000)
                await asyncio.sleep(2)  # 等待页面稳定
                
                # 获取页面文本
                text = await page.inner_text('body')
                
                # 解析数据
                data = parse_numbers_from_text(text, spot)
                print(f"       搜索指数: {data['search']}")
                print(f"       综合指数: {data['synth']}")
                
                results.append(data)
                
            except Exception as e:
                print(f"       ❌ 失败: {e}")
                results.append({"name": spot, "error": str(e)})
        
        print("\n[3] 保存数据...")
        
        output = {
            "date": "2026-04-11",
            "crawled_at": str(asyncio.get_event_loop().time),
            "competitors": results,
            "data_url": "抖音创作者平台(用户Chrome)"
        }
        
        with open("/tmp/crawl_data.json", "w") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("采集完成!")
        print("=" * 60)
        for r in results:
            print(f"  {r.get('name')}: 搜索={r.get('search')}, 综合={r.get('synth')}")
        
        print(f"\n数据已保存: /tmp/crawl_data.json")

if __name__ == "__main__":
    asyncio.run(main())
