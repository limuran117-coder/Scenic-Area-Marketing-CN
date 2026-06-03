#!/usr/bin/env python3
"""
竞品关键词深度分析 v4 - 带调试输出和页面滚动
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
        print("[CDP] 连接 OpenClaw Chrome...")
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
            await target_page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(5)
        else:
            print(f"使用已有页面: {target_page.url}")
            await target_page.bring_to_front()
            await asyncio.sleep(2)

        for i, keyword in enumerate(COMPETITORS):
            print(f"\n[{i+1}/{len(COMPETITORS)}] 搜索: {keyword}")
            try:
                # 用JS输入
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
                print(f"  JS输入结果: {res}")

                await target_page.keyboard.press("Enter")
                print("  等待数据加载...")

                # 等待足够时间让数据渲染
                await asyncio.sleep(6)

                # 滚动页面到底部，让懒加载数据触发
                await target_page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                await target_page.evaluate("() => window.scrollTo(0, 0)")
                await asyncio.sleep(1)

                # 获取页面文本
                page_text = await target_page.evaluate("() => document.body.innerText")

                # 打印调试信息
                if keyword in page_text:
                    # 找到关键词所在行
                    lines = page_text.split('\n')
                    for j, line in enumerate(lines):
                        if line.strip() == keyword:
                            # 打印关键词周围50行
                            start = max(0, j - 2)
                            end = min(len(lines), j + 30)
                            print(f"  [DEBUG] 关键词周围内容:")
                            for k in range(start, end):
                                print(f"    {k}: {lines[k][:80]}")
                            break
                else:
                    print(f"  [DEBUG] 关键词'{keyword}'未在页面文本中找到")

                # 解析
                data = parse_keyword_data(page_text, keyword)
                result["competitors"].append(data)

                print(f"  结果: 搜索={data['search_index']}, 综合={data['synth_index']}, "
                      f"内容={data['content_score']}, 互动={data['interaction_score']}")

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
    print(f"\n已保存: {filepath}")


async def main():
    print("=" * 60)
    print("竞品关键词深度分析 v4")
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
