#!/usr/bin/env python3
"""
竞品关键词分析 - 用URL参数导航，然后读DOM元素
"""

import json
import datetime
import asyncio
import os
import re
import urllib.parse

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
                print("Cookie加载成功")
            except Exception as e:
                print(f"Cookie加载失败: {e}")

        for i, keyword in enumerate(COMPETITORS):
            print(f"\n[{i+1}/{len(COMPETITORS)}] 搜索: {keyword}")
            try:
                # 用URL参数直接导航
                encoded_kw = urllib.parse.quote(keyword)
                search_url = f"https://creator.douyin.com/creator-micro/creator-count/arithmetic-index?keyword={encoded_kw}"

                # 找现有tab或创建新tab
                existing_page = None
                for pg in context.pages:
                    if 'arithmetic-index' in pg.url:
                        existing_page = pg
                        break

                if existing_page:
                    page = existing_page
                    await page.goto(search_url, timeout=30000)
                else:
                    page = await context.new_page()
                    await page.goto(search_url, timeout=30000)

                print(f"  导航到: {search_url}")

                # 等待页面加载
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(6)  # 等待6秒让数据加载

                # 截图
                await page.screenshot(path=f"/tmp/kw_result_{i+1}.png", full_page=False)
                print(f"  截图已保存")

                # 尝试读取页面数据 - 通过DOM属性
                # 方法1: 读取所有可见文本
                text = await page.evaluate("() => document.body.innerText")
                lines = text.split('\n')

                # 找关键词所在行
                keyword_lines = []
                for j, line in enumerate(lines):
                    if keyword in line or keyword[:6] in line:
                        keyword_lines.append((j, line))

                if keyword_lines:
                    print(f"  找到关键词匹配行: {keyword_lines[:3]}")
                    # 打印周围内容
                    for j, l in keyword_lines[:1]:
                        start = max(0, j - 2)
                        end = min(len(lines), j + 20)
                        for k in range(start, end):
                            print(f"    {k}: {lines[k][:80]}")
                else:
                    print(f"  关键词未在主文档找到")
                    # 打印前60行
                    print("  前60行:")
                    for j in range(min(60, len(lines))):
                        if lines[j].strip():
                            print(f"    {j}: {lines[j][:80]}")

                # 尝试用JS读取所有data属性
                data_attrs = await page.evaluate("""
                () => {
                    const results = [];
                    // 查找所有包含数字的文本节点
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    let node;
                    while (node = walker.nextNode()) {
                        const text = node.textContent.trim();
                        if (text && /\\d{3,}/.test(text)) {
                            results.push({
                                text: text.substring(0, 100),
                                parent: node.parentElement?.className?.substring(0, 50) || '',
                                tag: node.parentElement?.tagName || ''
                            });
                        }
                    }
                    return results.slice(0, 50);
                }
                """)
                print(f"  含数字的文本节点: {len(data_attrs)}")
                for da in data_attrs[:10]:
                    print(f"    [{da['tag']}] {da['text']}")

                # 解析数据 - 基于主文档文本
                data = parse_keyword_data(text, keyword)
                result["competitors"].append(data)
                print(f"  结果: 搜索={data['search_index']}, 综合={data['synth_index']}")

                if i < len(COMPETITORS) - 1:
                    print("  等待5秒...")
                    await asyncio.sleep(5)

            except Exception as e:
                print(f"  [错误] {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(5)
                continue

    return result


def parse_keyword_data(text, keyword):
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
        # 尝试部分匹配
        short_name = keyword[:6]
        if short_name not in text:
            return data
        match_text = text
    else:
        match_text = text

    lines = match_text.split('\n')
    keyword_idx = None
    for i, line in enumerate(lines):
        if keyword in line or (keyword[:6] in line and len(keyword) > 6):
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
    print(f"\n已保存: {filepath}")


async def main():
    print("=" * 60)
    print("竞品关键词深度分析")
    print("=" * 60)

    result = await crawl_keyword_index()

    if result and result.get("competitors"):
        save_data(result)
        print("\n✅ 采集完成！")
        for c in result["competitors"]:
            print(f"  {c['keyword']}: 搜索={c['search_index']}, 综合={c['synth_index']}, "
                  f"内容={c['content_score']}, 互动={c['interaction_score']}")
    else:
        print("⚠️ 无数据")
        save_data({
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "crawled_at": datetime.datetime.now().isoformat(),
            "note": "采集失败",
            "competitors": []
        })

    return result


if __name__ == "__main__":
    asyncio.run(main())
