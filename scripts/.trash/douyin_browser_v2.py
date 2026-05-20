#!/usr/bin/env python3
"""
抖音数据采集脚本 v2
使用OpenClaw的Chrome配置文件（保持登录状态）

数据来源：
- 整体数据：https://creator.douyin.com/creator-micro/creator-count/my-subscript
- 关键词搜索：https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
"""

import json
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

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

# OpenClaw浏览器配置
BROWSER_USER_DATA = Path.home() / ".openclaw/browser/openclaw/user-data"
COOKIE_FILE = "/tmp/juLiang_cookies.json"

async def crawl_with_browser():
    """使用OpenClaw浏览器配置采集数据"""
    results = []
    
    async with async_playwright() as p:
        # 启动Chromium，使用OpenClaw的user-data-dir
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_USER_DATA),
            headless=False,  # 有界面，方便调试
            args=['--start-maximized']
        )
        
        page = await browser.new_page()
        
        print("=" * 50)
        print("抖音数据采集 v2（使用OpenClaw浏览器）")
        print("=" * 50)
        
        # 1. 先访问整体数据页
        print("\n[1/2] 访问整体数据页...")
        try:
            await page.goto("https://creator.douyin.com/creator-micro/creator-count/my-subscript", timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(5)  # 等待页面完全加载
            
            # 获取页面文本
            content = await page.content()
            print(f"页面加载成功，长度: {len(content)} 字符")
            
            # 截图保存
            await page.screenshot(path="/tmp/douyin_overall.png")
            print("已保存截图: /tmp/douyin_overall.png")
            
        except Exception as e:
            print(f"整体页访问失败: {e}")
        
        # 2. 逐一搜索关键词
        print("\n[2/2] 逐一搜索关键词...")
        for spot in SCENIC_SPOTS:
            try:
                print(f"\n搜索: {spot}")
                
                # 访问关键词搜索页
                search_url = f"https://creator.douyin.com/creator-micro/creator-count/arithmetic-index?keyword={spot}"
                await page.goto(search_url, timeout=60000)
                await page.wait_for_load_state("networkidle", timeout=30000)
                await asyncio.sleep(3)
                
                # 获取页面文本
                text = await page.inner_text('body')
                print(f"  页面文本长度: {len(text)} 字符")
                
                # 截图
                await page.screenshot(path=f"/tmp/douyin_{spot}.png")
                print(f"  已保存: /tmp/douyin_{spot}.png")
                
                # 简单提取数据（搜索"搜索指数"后面的数字）
                search_index = "待解析"
                synth_index = "待解析"
                
                # 打印页面关键内容
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if '搜索指数' in line and i+1 < len(lines):
                        search_index = lines[i+1].strip()
                        print(f"  搜索指数: {search_index}")
                    if '综合指数' in line and i+1 < len(lines):
                        synth_index = lines[i+1].strip()
                        print(f"  综合指数: {synth_index}")
                
                results.append({
                    "name": spot,
                    "search": search_index,
                    "synth": synth_index,
                    "page_saved": f"/tmp/douyin_{spot}.png"
                })
                
            except Exception as e:
                print(f"  搜索失败: {e}")
                results.append({
                    "name": spot,
                    "error": str(e)
                })
        
        await browser.close()
    
    return results

async def main():
    print("开始采集...")
    results = await crawl_with_browser()
    
    print("\n" + "=" * 50)
    print("采集结果")
    print("=" * 50)
    for r in results:
        print(f"{r.get('name')}: 搜索={r.get('search')}, 综合={r.get('synth')}")
    
    # 保存结果
    output = {
        "date": "2026-04-11",  # 手动更新
        "crawled_at": asyncio.get_event_loop().time,
        "results": results,
        "note": "使用OpenClaw浏览器配置，需人工解析截图中的数据"
    }
    
    with open("/tmp/douyin_browser_v2.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存: /tmp/douyin_browser_v2.json")
    print("\n提示：请查看截图手动提取数据")

if __name__ == "__main__":
    asyncio.run(main())
