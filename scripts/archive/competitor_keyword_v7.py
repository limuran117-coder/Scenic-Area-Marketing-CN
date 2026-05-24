#!/usr/bin/env python3
"""
竞品关键词分析 v7 - 正确解析订阅页数据
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

# 缩写映射
ABBREV_MAP = {
    "建业电": "建业电影小镇",
    "万岁山": "万岁山武侠城",
    "清明上": "清明上河园",
    "只有河": "只有河南戏剧幻城",
    "郑州方": "郑州方特欢乐世界",
    "郑州海": "郑州海昌海洋公园",
    "郑州银": "郑州银基动物王国",
    "只有红": "只有红楼梦戏剧幻城"
}

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
        "source_url": "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator",
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

        # 找订阅页
        subscript_page = None
        for pg in context.pages:
            if 'my-subscript' in pg.url:
                subscript_page = pg
                break

        if not subscript_page:
            subscript_page = await context.new_page()
            await subscript_page.goto(
                "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator",
                timeout=30000
            )

        await subscript_page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(5)

        # 获取页面文本
        text = await subscript_page.evaluate("() => document.body.innerText")
        lines = text.split('\n')

        print(f"页面共 {len(lines)} 行")

        # 找到关键词区域（在我的订阅下面）
        # 关键词 -> 电脑端订阅 -> 站内信推送 -> 异动阈值20% -> 搜索指数 -> [有异动] -> 数字 -> 日环比 -> 数字% -> 综合指数 -> [有异动] -> 数字 -> 日环比 -> 数字%

        # 找到所有关键词名称行（精确匹配competitors中的名称）
        competitor_lines = {}
        for i, line in enumerate(lines):
            for comp in COMPETITORS:
                if line.strip() == comp:
                    competitor_lines[comp] = i

        print(f"找到 {len(competitor_lines)} 个关键词")

        # 对每个关键词，解析其后续20行的数据
        for comp, start_idx in competitor_lines.items():
            data = {
                "keyword": comp,
                "search_index": 0,
                "synth_index": 0,
                "content_score": 0,
                "interaction_score": 0,
                "search_trend": "",
                "synth_trend": ""
            }

            # 解析后续行
            section_end = start_idx + 30  # 每个关键词大约占30行
            if section_end > len(lines):
                section_end = len(lines)

            pending_value = None  # 存储"有异动"后面等待的数字

            for j in range(start_idx + 1, section_end):
                lbl = lines[j].strip()

                if lbl == "电脑端订阅" or lbl == "站内信推送" or lbl == "异动阈值 20%":
                    continue

                if lbl == "有异动":
                    pending_value = "有异动"  # 标记需要等待下一个数字
                    continue

                if lbl == "搜索指数":
                    pending_value = "搜索指数"
                    continue

                if lbl == "综合指数":
                    pending_value = "综合指数"
                    continue

                if lbl == "内容分":
                    pending_value = "内容分"
                    continue

                if lbl == "互动分":
                    pending_value = "互动分"
                    continue

                if lbl == "日环比":
                    pending_value = "日环比"
                    continue

                if lbl == "日环比" and j + 1 < section_end:
                    trend = lines[j + 1].strip()
                    if '%' in trend:
                        if pending_value == "搜索指数":
                            data["search_trend"] = trend
                        elif pending_value == "综合指数":
                            data["synth_trend"] = trend
                    pending_value = None
                    continue

                # 处理具体数值
                n = parse_number(lbl)
                if n > 0:
                    if pending_value == "有异动":
                        # 第一个数值是搜索指数
                        data["search_index"] = n
                        pending_value = None
                    elif pending_value == "搜索指数":
                        data["search_index"] = n
                        pending_value = None
                    elif pending_value == "综合指数":
                        data["synth_index"] = n
                        pending_value = None
                    elif pending_value == "内容分":
                        data["content_score"] = n
                        pending_value = None
                    elif pending_value == "互动分":
                        data["interaction_score"] = n
                        pending_value = None
                    continue

            result["competitors"].append(data)
            print(f"  {comp}: 搜索={data['search_index']}, 综合={data['synth_index']}, "
                  f"内容={data['content_score']}, 互动={data['interaction_score']}")

    return result


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
            print(f"  {c['keyword']}: 搜索={c['search_index']}, 综合={c['synth_index']}")
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
