#!/opt/homebrew/bin/python3.12
"""
竞品关键词深度分析 - 抖音关键词页采集
目标URL: https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
采集8个竞品关键词的：综合指数/搜索指数/内容分/互动分
⚠️ 每个关键词切换间隔5秒，页面完全加载后再操作
"""

import json
import datetime
import asyncio
import os
import re
import sys

# 竞品关键词列表
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
TARGET_URL = "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index"
OUTPUT_FILE = "/tmp/competitor_keyword_data.json"


async def parse_index_page(page_text, keyword):
    """解析关键词页数据"""
    data = {
        "keyword": keyword,
        "search_index": 0,
        "synth_index": 0,
        "content_score": 0,
        "interaction_score": 0,
        "search_trend": "",
        "synth_trend": ""
    }

    if keyword not in page_text:
        return data

    lines = page_text.split('\n')

    # 找到关键词所在行
    keyword_idx = None
    for i, line in enumerate(lines):
        if line.strip() == keyword:
            keyword_idx = i
            break

    if keyword_idx is None:
        return data

    # 在关键词区块内查找各指标
    # 已知页面结构：搜索指数、综合指数、内容分、互动分 四个指标
    metrics = {
        "搜索指数": "search_index",
        "综合指数": "synth_index",
        "内容分": "content_score",
        "互动分": "interaction_score"
    }

    trends = {
        "搜索指数": "search_trend",
        "综合指数": "synth_trend"
    }

    for i, line in enumerate(lines):
        lbl = line.strip()

        # 检查是否为指标标签
        if lbl in metrics:
            # 找该标签后的数字
            for j in range(i + 1, min(i + 6, len(lines))):
                val = lines[j].strip()
                if val == "有异动":
                    # 真实数据在下一行
                    for k in range(j + 1, min(k + 4, len(lines))):
                        v2 = lines[k].strip()
                        n = parse_number(v2)
                        if n > 0:
                            data[metrics[lbl]] = n
                            break
                    break
                n = parse_number(val)
                if n > 0:
                    data[metrics[lbl]] = n
                    break

        # 日环比趋势
        if lbl == "日环比" and i + 1 < len(lines):
            trend = lines[i + 1].strip()
            if '%' in trend:
                # 回溯确定是哪个指标
                for back in range(i - 1, max(i - 6, 0), -1):
                    prev = lines[back].strip()
                    if prev in trends:
                        data[trends[prev]] = trend
                        break

    return data


def parse_number(text):
    """从文本解析数字"""
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0


async def crawl_keyword_index():
    """采集竞品关键词指数"""
    from playwright.async_api import async_playwright

    today = datetime.date.today().strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "source_url": TARGET_URL,
        "competitors": []
    }

    async with async_playwright() as p:
        browser = None
        page = None

        # 策略1：连接 OpenClaw Chrome（port 18800）
        try:
            print("[CDP] 尝试连接 OpenClaw Chrome: http://127.0.0.1:18800")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
            print("[CDP] OpenClaw Chrome 连接成功！")
        except Exception as e:
            print(f"[CDP] OpenClaw Chrome 连接失败: {e}")

        # 策略2：连接本地已运行的 Chrome（9222端口）
        if not browser:
            try:
                print("[CDP] 尝试连接本地 Chrome: http://127.0.0.1:9222")
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("[CDP] 本地 Chrome 连接成功！")
            except Exception as e:
                print(f"[CDP] 本地 Chrome 连接失败: {e}")
                browser = None

        if not browser:
            print("[错误] 无法连接 Chrome，退出")
            return None

        # 获取 context
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
                print(f"已加载Cookie: {COOKIE_FILE}")
            except Exception as e:
                print(f"加载Cookie失败: {e}")

        page = await context.new_page()

        # 打开目标页面
        print(f"正在访问 {TARGET_URL} ...")
        await page.goto(TARGET_URL, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(5)  # 等待页面完全加载

        # 遍历搜索每个竞品关键词
        for i, keyword in enumerate(COMPETITORS):
            print(f"\n[{i+1}/{len(COMPETITORS)}] 搜索关键词: {keyword}")

            try:
                # 查找搜索框并输入关键词
                # 尝试多种选择器
                search_box = None
                selectors = [
                    'input[placeholder*="搜索"]',
                    'input[placeholder*="关键词"]',
                    '.search-input input',
                    'input[type="text"]'
                ]

                for sel in selectors:
                    try:
                        el = page.locator(sel).first
                        if await el.is_visible(timeout=2000):
                            search_box = el
                            print(f"  找到搜索框: {sel}")
                            break
                    except:
                        pass

                if not search_box:
                    # 截图调试
                    await page.screenshot(path=f"/tmp/search_box_error_{i+1}.png")
                    print(f"  [警告] 未找到搜索框，已截图保存")
                    continue

                # 清空并输入关键词
                await search_box.clear()
                await search_box.fill(keyword)
                print(f"  已输入关键词: {keyword}")

                # 按回车搜索
                await search_box.press("Enter")
                print(f"  按下回车，等待数据加载...")

                # 等待页面加载（networkidle 或指定元素出现）
                await asyncio.sleep(5)  # 严格遵守5秒间隔

                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass

                # 额外等待确保数据渲染
                await asyncio.sleep(3)

                # 获取页面文本
                try:
                    page_text = await page.evaluate("() => document.body.innerText")
                except:
                    page_text = await page.inner_text('body')

                # 解析数据
                spot_data = parse_index_page(page_text, keyword)
                result["competitors"].append(spot_data)

                print(f"  解析结果:")
                print(f"    搜索指数: {spot_data['search_index']}")
                print(f"    综合指数: {spot_data['synth_index']}")
                print(f"    内容分: {spot_data['content_score']}")
                print(f"    互动分: {spot_data['interaction_score']}")
                print(f"    搜索趋势: {spot_data['search_trend']}")
                print(f"    综合趋势: {spot_data['synth_trend']}")

                # 下一个关键词前等待5秒
                if i < len(COMPETITORS) - 1:
                    print(f"  等待5秒后搜索下一个...")
                    await asyncio.sleep(5)

            except Exception as e:
                print(f"  [错误] 采集 {keyword} 失败: {e}")
                import traceback
                traceback.print_exc()
                # 发生错误也等待5秒再继续
                await asyncio.sleep(5)
                continue

        # 关闭 Page
        await page.close()
        print("\n[完成] Page已关闭")

    return result


def save_data(data, filepath=OUTPUT_FILE):
    """保存数据到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {filepath}")


def main():
    print("=" * 60)
    print("竞品关键词深度分析 - 抖音关键词页采集")
    print(f"目标: {TARGET_URL}")
    print(f"竞品数量: {len(COMPETITORS)}")
    print("=" * 60)

    try:
        result = asyncio.run(crawl_keyword_index())

        if result and result.get("competitors"):
            save_data(result)
            print("\n✅ 采集成功！")
            # 打印摘要
            print("\n数据摘要:")
            for c in result["competitors"]:
                print(f"  {c['keyword']}: 搜索={c['search_index']}, 综合={c['synth_index']}, "
                      f"内容={c['content_score']}, 互动={c['interaction_score']}")
        else:
            print("\n⚠️ 采集数据为空")
            result = {
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "crawled_at": datetime.datetime.now().isoformat(),
                "note": "采集失败或无数据",
                "competitors": []
            }
            save_data(result)

    except Exception as e:
        print(f"\n[错误] 采集失败: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "crawled_at": datetime.datetime.now().isoformat(),
            "note": f"采集失败: {e}",
            "competitors": []
        }
        save_data(result)

    return result


if __name__ == "__main__":
    main()
