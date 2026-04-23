#!/usr/bin/env python3
"""
竞品关键词分析 - 从订阅页读取数据
订阅页URL: https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator
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
                print("Cookie加载成功")
            except Exception as e:
                print(f"Cookie加载失败: {e}")

        # 找订阅页
        subscript_page = None
        for pg in context.pages:
            if 'my-subscript' in pg.url:
                subscript_page = pg
                break

        if subscript_page:
            print(f"使用订阅页: {subscript_page.url}")
            await subscript_page.bring_to_front()
        else:
            subscript_page = await context.new_page()
            await subscript_page.goto(
                "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator",
                timeout=30000
            )
            print("新建订阅页")

        await subscript_page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(5)

        # 截图
        await subscript_page.screenshot(path="/tmp/subscript_page.png", full_page=False)
        print("截图已保存: /tmp/subscript_page.png")

        # 获取主文档文本
        text = await subscript_page.evaluate("() => document.body.innerText")
        lines = text.split('\n')

        print(f"\n页面文本: {len(text)} 字符, {len(lines)} 行")

        # 找到"我的订阅"部分
        my_sub_idx = None
        for i, line in enumerate(lines):
            if '我的订阅' in line:
                my_sub_idx = i
                break

        if my_sub_idx is not None:
            print(f"找到'我的订阅'在行 {my_sub_idx}")
            # 打印周围内容
            for j in range(my_sub_idx, min(my_sub_idx + 80, len(lines))):
                if lines[j].strip():
                    print(f"  {j}: {lines[j][:100]}")

        # 尝试获取所有竞品的数字数据
        # 先用简单方式：找所有3位以上的数字
        all_numbers = []
        for i, line in enumerate(lines):
            n = parse_number(line.strip())
            if n > 1000:  # 只取大于1000的（指数通常是几千）
                all_numbers.append((i, n, lines[i][:80]))

        print(f"\n找到 {len(all_numbers)} 个数字:")
        for i, n, ctx in all_numbers[:30]:
            print(f"  行{i}: {n} ({ctx})")

        # 解析数据 - 尝试从"我的订阅"区域提取
        # 该区域结构大概是：关键词、有异动、搜索指数、数值、综合指数、数值
        data_list = []
        in_sub_section = False
        sub_lines = []

        for i, line in enumerate(lines):
            if '我的订阅' in line:
                in_sub_section = True
            if in_sub_section:
                sub_lines.append((i, line))
                if '抖音实时热点' in line:
                    break

        print(f"\n'我的订阅'区域共 {len(sub_lines)} 行")

        # 解析：每个关键词占据一个小区块
        # 结构：[缩写的关键词名, 有异动/无, 搜索指数, 数值, 综合指数, 数值, 日环比, 数值]
        current_kw = None
        kw_data = {}

        for i, line in enumerate(sub_lines):
            lbl = line[1].strip()
            if not lbl:
                continue

            # 跳过标题
            if lbl in ['我的订阅', '更多', '抖音实时热点', '排名', '热点名称',
                       '热点指数', '热点指数变化', '抖音飙升热点']:
                continue

            # 关键词缩写匹配（3-6个字符+省略号）
            if '...' in lbl and len(lbl) <= 10 and '有异动' not in lbl:
                # 保存上一个关键词
                if current_kw and kw_data:
                    data_list.append(kw_data)
                    kw_data = {}

                # 找完整名称
                full_name = find_full_name(lbl, COMPETITORS)
                current_kw = full_name
                kw_data = {"keyword": full_name, "abbrev": lbl}
                print(f"  发现关键词: {lbl} -> {full_name}")
                continue

            # 有异动标记
            if lbl == '有异动':
                kw_data['has_change'] = True
                continue

            # 日环比
            if lbl == '日环比' and i + 1 < len(sub_lines):
                trend = sub_lines[i + 1][1].strip()
                kw_data['trend'] = trend
                continue

            # 搜索指数
            if lbl == '搜索指数' and current_kw:
                # 找下一个数字
                for j in range(i + 1, min(i + 5, len(sub_lines))):
                    n = parse_number(sub_lines[j][1].strip())
                    if n > 0:
                        kw_data['search_index'] = n
                        break
                continue

            # 综合指数
            if lbl == '综合指数' and current_kw:
                for j in range(i + 1, min(i + 5, len(sub_lines))):
                    n = parse_number(sub_lines[j][1].strip())
                    if n > 0:
                        kw_data['synth_index'] = n
                        break
                continue

            # 内容分
            if lbl == '内容分' and current_kw:
                for j in range(i + 1, min(i + 5, len(sub_lines))):
                    n = parse_number(sub_lines[j][1].strip())
                    if n > 0:
                        kw_data['content_score'] = n
                        break
                continue

            # 互动分
            if lbl == '互动分' and current_kw:
                for j in range(i + 1, min(i + 5, len(sub_lines))):
                    n = parse_number(sub_lines[j][1].strip())
                    if n > 0:
                        kw_data['interaction_score'] = n
                        break
                continue

        # 保存最后一个
        if current_kw and kw_data:
            data_list.append(kw_data)

        print(f"\n解析出 {len(data_list)} 个关键词数据:")
        for d in data_list:
            print(f"  {d}")

        # 整理数据
        for kw_data in data_list:
            result["competitors"].append({
                "keyword": kw_data.get("keyword", ""),
                "abbrev": kw_data.get("abbrev", ""),
                "search_index": kw_data.get("search_index", 0),
                "synth_index": kw_data.get("synth_index", 0),
                "content_score": kw_data.get("content_score", 0),
                "interaction_score": kw_data.get("interaction_score", 0),
                "trend": kw_data.get("trend", ""),
                "has_change": kw_data.get("has_change", False)
            })

    return result


def find_full_name(abbrev, competitors):
    """通过缩写找完整名称"""
    # 去掉省略号
    short = abbrev.replace('...', '')
    for comp in competitors:
        if comp.startswith(short):
            return comp
    return abbrev


def save_data(data, filepath=OUTPUT_FILE):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {filepath}")


async def main():
    print("=" * 60)
    print("竞品关键词分析 - 从订阅页读取")
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
