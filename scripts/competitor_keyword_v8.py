#!/usr/bin/env python3
"""
竞品关键词分析 v8 - 精确标签索引解析
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

        text = await subscript_page.evaluate("() => document.body.innerText")
        lines = text.split('\n')

        # 找到所有关键词行的索引
        kw_positions = {}  # {关键词名: 行号}
        for i, line in enumerate(lines):
            for comp in COMPETITORS:
                if line.strip() == comp:
                    kw_positions[comp] = i

        print(f"找到 {len(kw_positions)} 个关键词")

        # 对每个关键词，按顺序解析其后续数据
        # 每个关键词区块结构：
        # 关键词行
        # 电脑端订阅
        # 站内信推送
        # 异动阈值 20%
        # 搜索指数
        # [有异动]
        # 数值
        # 日环比
        # 数值%
        # 综合指数
        # [有异动]
        # 数值
        # 日环比
        # 数值%
        # (下一个关键词...)

        keywords_sorted = sorted(kw_positions.items(), key=lambda x: x[1])

        for idx, (comp, kw_idx) in enumerate(keywords_sorted):
            data = {
                "keyword": comp,
                "search_index": 0,
                "synth_index": 0,
                "content_score": 0,
                "interaction_score": 0,
                "search_trend": "",
                "synth_trend": ""
            }

            # 确定区块范围：到这个关键词或结尾
            next_kw_idx = keywords_sorted[idx + 1][1] if idx + 1 < len(keywords_sorted) else len(lines)

            # 打印区块内容用于调试
            section = lines[kw_idx:next_kw_idx]
            print(f"\n--- {comp} (行{kw_idx}-{next_kw_idx-1}) ---")
            for si, sline in enumerate(section[:25]):
                if sline.strip():
                    print(f"  {kw_idx + si}: {sline[:80]}")

            # 找搜索指数和综合指数
            # 策略：找"搜索指数"标签，然后找后面第一个数字（跳过"有异动"）
            # 找"综合指数"标签，然后找后面第一个数字（跳过"有异动"）

            pending_metric = None  # 当前等待的指标类型

            for ji, jline in enumerate(section):
                lbl = jline.strip()

                # 指标标签
                if lbl == "搜索指数":
                    pending_metric = "search"
                    continue
                elif lbl == "综合指数":
                    pending_metric = "synth"
                    continue

                # 有异动 - 标记但不跳
                if lbl == "有异动":
                    # 继续，下一个数字还是属于这个指标
                    continue

                # 日环比
                if lbl == "日环比":
                    pending_metric = None  # 忽略日环比的数值
                    continue

                # 数值行
                n = parse_number(lbl)
                if n > 0 and pending_metric:
                    if pending_metric == "search" and data["search_index"] == 0:
                        data["search_index"] = n
                    elif pending_metric == "synth" and data["synth_index"] == 0:
                        data["synth_index"] = n
                    pending_metric = None  # 只取第一个数值
                    continue

                # 忽略其他行（电脑端订阅、站内信推送、异动阈值等）
                if lbl in ["电脑端订阅", "站内信推送", "异动阈值 20%"]:
                    continue

            result["competitors"].append(data)
            print(f"  => 搜索={data['search_index']}, 综合={data['synth_index']}")

    return result


def save_data(data, filepath=OUTPUT_FILE):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {filepath}")


async def main():
    print("=" * 60)
    print("竞品关键词深度分析 v8")
    print("=" * 60)

    result = await crawl_keyword_index()

    if result and result.get("competitors"):
        save_data(result)
        print("\n✅ 最终结果:")
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
