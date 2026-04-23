#!/usr/bin/env python3
"""
竞品关键词深度分析 - 抖音关键词页采集
使用 CDP 直连 OpenClaw Chrome (port 18800)
⚠️ 每个关键词切换间隔5秒
"""

import json
import datetime
import asyncio
import os
import re

COMPETITORS = [
    "建业电影小镇",
    "万岁山武侠城",
    "清明上河园",
    "只有河南戏剧幻城",
    "郑州方特欢乐世界",
    "郑州海昌海洋公园",
    "郑州银基动物王国",
    "只有红楼梦戏剧幻城"
]

COOKIE_FILE = "/tmp/juLiang_cookies.json"
OUTPUT_FILE = "/tmp/competitor_keyword_data.json"


def parse_number(text):
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0


async def parse_page(page):
    """从页面提取关键词数据"""
    try:
        text = await page.evaluate("() => document.body.innerText")
    except:
        text = await page.inner_text('body')
    return text


async def crawl_keyword_index():
    from playwright.async_api import async_playwright

    today = datetime.date.today().strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "source_url": "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index",
        "competitors": []
    }

    async with async_playwright() as p:
        # 连接 OpenClaw Chrome
        try:
            print("[CDP] 连接 OpenClaw Chrome: http://127.0.0.1:18800")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
            print("[CDP] 连接成功")
        except Exception as e:
            print(f"[CDP] 连接失败: {e}")
            return None

        # 获取已有的 page（browser 是 Browser 对象）
        if hasattr(browser, 'contexts'):
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
        else:
            context = browser

        # 加载 Cookie
        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                print("Cookie加载成功")
            except Exception as e:
                print(f"Cookie加载失败: {e}")

        # 查找关键词页的 tab
        page = None
        for p_item in context.pages:
            url = p_item.url
            if 'arithmetic-index' in url or 'creator-count' in url:
                page = p_item
                print(f"找到目标页面: {url}")
                break

        if not page:
            # 如果没有找到，创建新页面
            page = await context.new_page()
            await page.goto("https://creator.douyin.com/creator-micro/creator-count/arithmetic-index",
                          timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(5)

        for i, keyword in enumerate(COMPETITORS):
            print(f"\n[{i+1}/{len(COMPETITORS)}] 搜索: {keyword}")
            try:
                # 等待搜索框出现
                search_box = page.locator('input[placeholder*="输入"]').first
                await search_box.wait_for(timeout=5000)

                # 点击清空并输入
                await search_box.click()
                await asyncio.sleep(0.5)

                # 清空现有内容
                await page.keyboard.press("Control+A")
                await asyncio.sleep(0.2)
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.3)

                # 输入关键词
                await search_box.fill(keyword)
                print(f"  已输入: {keyword}")

                # 按回车
                await page.keyboard.press("Enter")
                print("  等待数据加载...")

                # 等待页面加载
                await asyncio.sleep(6)  # 严格6秒等待

                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass

                # 获取页面文本
                page_text = await parse_page(page)

                # 解析数据
                data = parse_keyword_data(page_text, keyword)
                result["competitors"].append(data)

                print(f"  搜索指数: {data['search_index']}")
                print(f"  综合指数: {data['synth_index']}")
                print(f"  内容分: {data['content_score']}")
                print(f"  互动分: {data['interaction_score']}")

                # 下一个前等待5秒
                if i < len(COMPETITORS) - 1:
                    print("  等待5秒...")
                    await asyncio.sleep(5)

            except Exception as e:
                print(f"  [错误] {keyword}: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(5)
                continue

    return result


def parse_keyword_data(text, keyword):
    """解析关键词数据"""
    data = {
        "keyword": keyword,
        "search_index": 0,
        "synth_index": 0,
        "content_score": 0,
        "interaction_score": 0,
        "search_trend": "",
        "synth_trend": ""
    }

    if keyword not in text:
        return data

    lines = text.split('\n')
    keyword_idx = None
    for i, line in enumerate(lines):
        if line.strip() == keyword:
            keyword_idx = i
            break

    if keyword_idx is None:
        return data

    metrics = {
        "搜索指数": "search_index",
        "综合指数": "synth_index",
        "内容分": "content_score",
        "互动分": "interaction_score"
    }

    trends = {"搜索指数": "search_trend", "综合指数": "synth_trend"}

    for i, line in enumerate(lines):
        lbl = line.strip()

        if lbl in metrics:
            for j in range(i + 1, min(i + 6, len(lines))):
                val = lines[j].strip()
                if val == "有异动":
                    for k in range(j + 1, min(j + 4, len(lines))):
                        n = parse_number(lines[k].strip())
                        if n > 0:
                            data[metrics[lbl]] = n
                            break
                    break
                n = parse_number(val)
                if n > 0:
                    data[metrics[lbl]] = n
                    break

        if lbl == "日环比" and i + 1 < len(lines):
            trend = lines[i + 1].strip()
            if '%' in trend:
                for back in range(i - 1, max(i - 6, 0), -1):
                    prev = lines[back].strip()
                    if prev in trends:
                        data[trends[prev]] = trend
                        break

    return data


def save_data(data, filepath=OUTPUT_FILE):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存: {filepath}")


async def main():
    print("=" * 60)
    print("竞品关键词深度分析")
    print("=" * 60)

    result = await crawl_keyword_index()

    if result and result.get("competitors"):
        save_data(result)
        print("\n✅ 采集完成！")
        print("\n数据摘要:")
        for c in result["competitors"]:
            print(f"  {c['keyword']}: 搜索={c['search_index']}, 综合={c['synth_index']}, "
                  f"内容={c['content_score']}, 互动={c['interaction_score']}")
    else:
        print("⚠️ 采集数据为空")
        result = {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "crawled_at": datetime.datetime.now().isoformat(),
            "note": "采集失败或无数据",
            "competitors": []
        }
        save_data(result)

    return result


if __name__ == "__main__":
    asyncio.run(main())
