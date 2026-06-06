#!/opt/homebrew/bin/python3.12
"""
抖音指数数据采集脚本 v11
使用 Playwright CDP 连接已登录浏览器，从「我的订阅」页面批量采集景区数据。
无需逐个搜索，一个页面完成 8 个景区的搜索指数 + 综合指数 + 日环比。

数据来源: https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator
备选(关键词搜索): https://creator.douyin.com/creator-micro/creator-count/arithmetic-index

景区列表:
1. 建业电影小镇  2. 万岁山武侠城  3. 清明上河园  4. 只有河南戏剧幻城
5. 郑州方特欢乐世界  6. 郑州海昌海洋公园  7. 郑州银基动物王国  8. 只有红楼梦戏剧幻城

输出: /tmp/crawl_data.json
Cookie: /tmp/juLiang_cookies.json
"""
import asyncio, json, os, re, sys, datetime, time

CRAWL_URL = "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator"
SEARCH_URL = "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index"
CDP_URL = "http://127.0.0.1:18800"
COOKIE_FILE = "/tmp/juLiang_cookies.json"
OUTPUT = "/tmp/crawl_data.json"
LOCK_PATH = "/tmp/douyin_crawl.lock"

ALL_SPOTS = [
    "建业电影小镇", "万岁山武侠城", "清明上河园", "只有河南戏剧幻城",
    "郑州方特欢乐世界", "郑州海昌海洋公园", "郑州银基动物王国", "只有红楼梦戏剧幻城"
]


def parse_subscription_text(page_text):
    """从「我的订阅」页面文本中解析所有景区数据"""
    # 页面文本格式:
    # 景区名称
    # 电脑端订阅 站内信推送 异动阈值 20%
    # 搜索指数 [有异动] 数字 日环比 [+/-]百分比
    # 综合指数 [有异动] 数字 日环比 [+/-]百分比
    results = []
    lines = page_text.split('\n')

    for spot in ALL_SPOTS:
        data = {"name": spot, "search": 0, "synth": 0, "search_trend": "", "synth_trend": "", "anomaly": False}
        if spot not in page_text:
            results.append(data)
            continue

        # Find the spot in lines
        for i, line in enumerate(lines):
            if line.strip() == spot:
                block = lines[i:i + 15]
                block_text = '\n'.join(block)

                # Parse search index
                search_match = re.search(r'搜索指数\s*(?:有异动)?\s*([\d,]+)\s*日环比\s*([+-]?[\d.]+%)', block_text)
                synth_match = re.search(r'综合指数\s*(?:有异动)?\s*([\d,]+)\s*日环比\s*([+-]?[\d.]+%)', block_text)

                if search_match:
                    data["search"] = int(search_match.group(1).replace(',', ''))
                    data["search_trend"] = search_match.group(2)
                if synth_match:
                    data["synth"] = int(synth_match.group(1).replace(',', ''))
                    data["synth_trend"] = synth_match.group(2)

                if "有异动" in block_text:
                    data["anomaly"] = True
                break

        results.append(data)

    return results


async def crawl():
    from playwright.async_api import async_playwright

    today = datetime.date.today().strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "source": "my-subscript",
        "competitors": [],
        "error": None
    }

    # 互斥锁
    try:
        lock_fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        age = time.time() - os.path.getmtime(LOCK_PATH)
        if age > 120:
            os.remove(LOCK_PATH)
            lock_fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL)
        else:
            msg = f"上一个采集实例还在运行({age:.0f}s)，跳过"
            print(f"[⏳] {msg}")
            result["error"] = msg
            return result

    try:
        async with async_playwright() as p:
            # CDP 连接
            print(f"[CDP] 连接 {CDP_URL}")
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print("[CDP] 连接成功")

            # 获取页面
            pages = browser.contexts[0].pages if browser.contexts else []
            if not pages:
                raise Exception("无可用页面")

            # 找已有订阅页或新建
            target = None
            for page in pages:
                if "my-subscript" in page.url:
                    target = page
                    print(f"[✓] 找到订阅页: {page.url[:70]}")
                    break

            if not target:
                target = pages[0]
                print("[!] 未找到订阅页，使用当前页")
                
            await target.bring_to_front()
            await target.goto(CRAWL_URL, wait_until="networkidle", timeout=30000)
            print("[✓] 订阅页加载完成")

            # 等待数据渲染
            await asyncio.sleep(3)

            # 读取页面文本
            page_text = await target.evaluate("() => document.body.innerText")
            text_len = len(page_text)
            print(f"[📄] 页面文本: {text_len} 字符")

            # 解析数据
            spots = parse_subscription_text(page_text)
            result["competitors"] = spots

            # 🖼️ 多模态截图（v11+）: 保存订阅页截图供日报M3分析
            screenshot_path = "/tmp/douyin_screenshot.png"
            try:
                await target.screenshot(path=screenshot_path, full_page=True)
                result["screenshot"] = screenshot_path
                print(f"[🖼️] 截图已存: {screenshot_path}")
            except Exception as e:
                print(f"[⚠️] 截图失败: {e}")
                result["screenshot"] = None

            # 输出
            print(f"\n{'='*60}")
            print(f"  抖音指数日报 · {today}")
            print(f"{'='*60}")
            print(f"{'景区':<16} {'搜索指数':>8} {'日环比':>10} {'综合指数':>8} {'日环比':>10}")
            print(f"{'-'*56}")
            for s in spots:
                anom = " ⚠" if s["anomaly"] else ""
                print(f"{s['name']:<16} {s['search']:>8,} {s['search_trend']:>10} {s['synth']:>8,} {s['synth_trend']:>10}{anom}")

            # 保存
            with open(OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n[💾] 已保存: {OUTPUT}")

            # 同步 Cookie
            try:
                cookies = await target.context.cookies()
                douyin_cookies = [c for c in cookies if 'douyin' in c.get('domain','') or 'bytedance' in c.get('domain','')]
                with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(douyin_cookies, f, ensure_ascii=False, indent=2)
                print(f"[🍪] Cookie 同步: {len(douyin_cookies)} 条 → {COOKIE_FILE}")
            except Exception as e:
                print(f"[⚠️] Cookie 同步失败: {e}")

            await browser.close()
            print("[✅] 采集完成")
            return result

    except Exception as e:
        print(f"[❌] 采集异常: {e}")
        result["error"] = str(e)
        return result
    finally:
        try:
            os.close(lock_fd)
            os.remove(LOCK_PATH)
        except:
            pass


if __name__ == "__main__":
    ts = time.strftime("%Y-%m-%d %H:%M")
    print(f"=== 抖音指数采集 [{ts}] ===")
    r = asyncio.run(crawl())
    if r and r.get("competitors"):
        success = sum(1 for s in r["competitors"] if s["search"] > 0)
        print(f"\n结果: {success}/{len(r['competitors'])} 景区数据有效")
    sys.exit(0 if r and r.get("competitors") else 1)
