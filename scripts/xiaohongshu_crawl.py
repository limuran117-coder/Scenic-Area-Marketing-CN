#!/usr/bin/env python3
"""
小红书数据采集脚本 v2
使用Playwright + 已有CDP浏览器连接

用法：
  python3 scripts/xiaohongshu_crawl.py "关键词" [CDP端口默认18800]

输出：/tmp/xiaohongshu_关键词.json
"""

import json
import datetime
import asyncio
import sys
import os
import re
from playwright.async_api import async_playwright

CDP_HOST = "http://127.0.0.1"
DEFAULT_CDP_PORT = 18800

def parse_args():
    """解析命令行参数"""
    keyword = sys.argv[1] if len(sys.argv) > 1 else "建业电影小镇"
    cdp_port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CDP_PORT
    return keyword, cdp_port

def extract_data_from_page(text: str, content: str) -> dict:
    """从页面提取数据（简化版）"""
    # 提取笔记数量
    notes_match = re.search(r'约(\d+)万篇|(\d+)篇笔记', text)
    notes_count = notes_match.group(1) or notes_match.group(2) if notes_match else "—"

    # 提取互动数据
    likes_match = re.findall(r'(\d+\.?\d*万|\d+)赞', text)
    top_likes = likes_match[:5] if likes_match else []

    return {
        "notes_approx": notes_count,
        "top_likes": top_likes,
        "content_length": len(content)
    }

async def search_keyword(cdp_url: str, keyword: str, timeout: int = 30000) -> dict:
    """用CDP连接已有浏览器，搜索关键词"""
    result = {
        "keyword": keyword,
        "success": False,
        "error": None,
        "data": {}
    }

    try:
        async with async_playwright() as p:
            # 连接已有CDP浏览器（不是launch新浏览器！）
            browser = await p.chromium.connect_over_cdp(cdp_url)
            
            # 列出所有tab，找一个可用的
            target_tab = None
            for ctx in browser.contexts:
                for i, pg in enumerate(ctx.pages):
                    try:
                        url = pg.url
                        if url and not url.startswith("chrome://"):
                            target_tab = pg
                            print(f"  → 使用Tab{i}: {url[:60]}", flush=True)
                            break
                    except:
                        continue
                if target_tab:
                    break

            if not target_tab:
                # 没有可用Tab，创建新的
                for ctx in browser.contexts:
                    target_tab = await ctx.new_page()
                    break

            page = target_tab

            # 导航到小红书搜索结果页
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed"
            print(f"  → 打开: {search_url}", flush=True)
            
            response = await page.goto(search_url, timeout=timeout, wait_until="domcontentloaded")
            
            if response and response.status in [302, 301]:
                print(f"  → 重定向到登录页，跳过", flush=True)
                result["error"] = "redirect_to_login"
                await browser.close()
                return result
            
            # 等待内容加载
            await asyncio.sleep(3)
            
            # 滚动一下触发懒加载
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(2)
            
            # 获取页面文本
            text = await page.inner_text("body")
            content = await page.content()
            
            # 提取数据
            result["data"] = extract_data_from_page(text, content)
            result["success"] = True
            print(f"  ✓ {keyword}: 获取内容{len(content)}字节", flush=True)
            
            await browser.close()

    except Exception as e:
        result["error"] = str(e)[:100]
        print(f"  ✗ 失败: {e}", flush=True)

    return result

async def main():
    keyword, cdp_port = parse_args()
    cdp_url = f"{CDP_HOST}:{cdp_port}"
    
    print("=" * 50, flush=True)
    print(f"小红书数据采集 | 关键词: {keyword} | CDP: {cdp_port}", flush=True)
    print("=" * 50, flush=True)
    
    # 尝试连接CDP
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(cdp_url, timeout=5000)
            await browser.close()
            print("✓ CDP连接成功\n", flush=True)
    except Exception as e:
        print(f"✗ CDP连接失败: {e}", flush=True)
        print("  请确认专属浏览器已启动（--remote-debugging-port=18800）", flush=True)
        sys.exit(1)
    
    # 采集数据
    result = await search_keyword(cdp_url, keyword)
    
    # 保存
    output_file = f"/tmp/xiaohongshu_{keyword}.json"
    output = {
        "keyword": keyword,
        "crawled_at": datetime.datetime.now().isoformat(),
        "success": result["success"],
        "error": result.get("error"),
        "data": result.get("data", {})
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'✓' if result['success'] else '✗'} 已保存: {output_file}", flush=True)
    return output

if __name__ == "__main__":
    asyncio.run(main())
