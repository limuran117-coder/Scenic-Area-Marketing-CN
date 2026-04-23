#!/usr/bin/env python3
"""
调试版本2 - 检查iframe和完整HTML
"""

import json
import datetime
import asyncio
import os
import re
import urllib.parse

COMPETITORS = ["建业电影小镇", "万岁山武侠城"]
COOKIE_FILE = "/tmp/juLiang_cookies.json"


async def debug_iframe():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        print("[CDP] 连接...")
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        except Exception as e:
            print(f"[CDP] 连接失败: {e}")
            return

        context = browser.contexts[0] if browser.contexts else await browser.new_context()

        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
            except:
                pass

        # 找 arithmetic-index 页面
        target_page = None
        for pg in context.pages:
            if 'arithmetic-index' in pg.url:
                target_page = pg
                break

        if not target_page:
            target_page = await context.new_page()
            await target_page.goto(
                "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index",
                timeout=30000
            )
            await asyncio.sleep(5)
        else:
            print(f"当前页面: {target_page.url}")
            await target_page.bring_to_front()
            await asyncio.sleep(2)

        # 检查iframe
        iframe_info = await target_page.evaluate("""
        () => {
            const iframes = [];
            const frames = window.frames;
            for (let i = 0; i < frames.length; i++) {
                try {
                    const doc = frames[i].document;
                    if (doc && doc.body) {
                        iframes.push({
                            name: frames[i].name || 'unnamed',
                            src: frames[i].location.href,
                            bodyText: doc.body.innerText.substring(0, 2000)
                        });
                    }
                } catch(e) {
                    iframes.push({name: frames[i].name || 'unnamed', error: e.message});
                }
            }
            return iframes;
        }
        """)

        print(f"\n发现 {len(iframe_info)} 个iframe:")
        for i, info in enumerate(iframe_info):
            print(f"\n--- iframe {i} ---")
            if 'error' in info:
                print(f"  错误: {info['error']}")
            else:
                print(f"  名称: {info.get('name')}")
                print(f"  URL: {info.get('src')}")
                text = info.get('bodyText', '')
                print(f"  内容前500字符: {text[:500]}")

        # 直接用URL参数搜索
        print("\n\n=== 直接用URL参数搜索 ===")
        keyword = "建业电影小镇"
        encoded_kw = urllib.parse.quote(keyword)
        search_url = f"https://creator.douyin.com/creator-micro/creator-count/arithmetic-index?keyword={encoded_kw}"
        print(f"访问: {search_url}")

        # 在新tab打开
        page2 = await context.new_page()
        await page2.goto(search_url, timeout=30000)
        await page2.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(5)

        # 截图
        await page2.screenshot(path="/tmp/direct_url_search.png", full_page=False)
        print("截图已保存: /tmp/direct_url_search.png")

        # 获取文本
        text = await page2.evaluate("() => document.body.innerText")
        print(f"\n页面文本长度: {len(text)} 字符")
        lines = text.split('\n')
        print(f"行数: {len(lines)}")

        # 打印前80行
        print("\n--- 页面文本前80行 ---")
        for j, line in enumerate(lines[:80]):
            if line.strip():
                print(f"  {j}: {line[:100]}")

        # 检查数据
        for kw in ["搜索指数", "综合指数", "内容分", "互动分", "建业电影小镇"]:
            if kw in text:
                print(f"✅ 找到'{kw}'")
            else:
                print(f"❌ 未找到'{kw}'")

        await page2.close()

    return None


async def main():
    await debug_iframe()


if __name__ == "__main__":
    asyncio.run(main())
