#!/usr/bin/env python3
"""调试版本 - 打印完整页面文本和截图"""

import json
import datetime
import asyncio
import os
import re

COMPETITORS = ["建业电影小镇"]

COOKIE_FILE = "/tmp/juLiang_cookies.json"
OUTPUT_FILE = "/tmp/competitor_keyword_debug.json"


def parse_number(text):
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0


async def crawl_keyword_index():
    from playwright.async_api import async_playwright

    today = datetime.date.today().strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "competitors": []
    }

    async with async_playwright() as p:
        print("[CDP] 连接...")
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        except Exception as e:
            print(f"[CDP] 连接失败: {e}")
            return None

        context = browser.contexts[0] if browser.contexts else await browser.new_context()

        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
            except:
                pass

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
            await target_page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(5)
        else:
            print(f"页面: {target_page.url}")
            await target_page.bring_to_front()
            await asyncio.sleep(2)

        keyword = COMPETITORS[0]
        print(f"\n搜索: {keyword}")

        # 输入
        input_js = f"""
        () => {{
            const inputs = document.querySelectorAll('input');
            for (const inp of inputs) {{
                if (inp.placeholder && inp.placeholder.includes('请输入')) {{
                    inp.value = '{keyword}';
                    inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return 'ok';
                }}
            }}
            return 'not found';
        }}
        """
        res = await target_page.evaluate(input_js)
        print(f"输入结果: {res}")

        await target_page.keyboard.press("Enter")
        print("等待...")
        await asyncio.sleep(8)

        # 截图
        await target_page.screenshot(path="/tmp/keyword_search_result.png", full_page=False)
        print("截图已保存: /tmp/keyword_search_result.png")

        # 获取完整文本 - 包括所有iframe
        all_text = await target_page.evaluate("""
        () => {
            // 获取主文档文本
            let text = document.body.innerText;
            
            // 获取所有iframe的文本
            const iframes = document.querySelectorAll('iframe');
            for (const iframe of iframes) {
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                    if (iframeDoc) {
                        text += '\\n[IFRAME]\\n' + iframeDoc.body.innerText;
                    }
                } catch(e) {}
            }
            
            return text;
        }
        """)

        # 打印页面文本前300行
        lines = all_text.split('\n')
        print(f"\n页面文本总长度: {len(all_text)} 字符, {len(lines)} 行")
        print("\n--- 页面文本前100行 ---")
        for j, line in enumerate(lines[:100]):
            if line.strip():
                print(f"  {j}: {line[:100]}")

        # 查找关键词附近内容
        if keyword in all_text:
            for j, line in enumerate(lines):
                if keyword in line:
                    start = max(0, j - 3)
                    end = min(len(lines), j + 30)
                    print(f"\n--- 关键词'{keyword}'附近内容 (行{start}-{end}) ---")
                    for k in range(start, end):
                        print(f"  {k}: {lines[k][:120]}")
                    break
        else:
            print(f"\n关键词'{keyword}'未找到，搜索URL中的其他关键词")
            # 尝试从URL中提取
            url = target_page.url
            print(f"当前URL: {url}")
            if 'keyword=' in url:
                import urllib.parse
                kw = urllib.parse.unquote(url.split('keyword=')[1].split('&')[0])
                print(f"URL中的关键词: {kw}")

        # 也检查是否有综合指数等数据
        data_indicators = ["搜索指数", "综合指数", "内容分", "互动分"]
        for indicator in data_indicators:
            if indicator in all_text:
                print(f"✅ 找到'{indicator}'")
            else:
                print(f"❌ 未找到'{indicator}'")

    return result


async def main():
    result = await crawl_keyword_index()
    return result


if __name__ == "__main__":
    asyncio.run(main())
