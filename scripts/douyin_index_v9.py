#!/usr/bin/env python3
"""
抖音指数数据采集脚本 v9
使用Playwright浏览器自动化采集抖音创作者平台数据
支持Cookie持久化登录态

数据订阅页面(已订阅景区概览):
https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator

景区列表:
1. 建业电影小镇
2. 万岁山武侠城
3. 清明上河园
4. 只有河南戏剧幻城
5. 郑州方特欢乐世界
6. 郑州海昌海洋公园
7. 郑州银基动物王国
8. 只有红楼梦戏剧幻城

输出:/tmp/crawl_data.json
Cookie存储:/tmp/juLiang_cookies.json
"""

import json
import datetime
import asyncio
import os
import glob
import sys
import re
import subprocess

def cleanup_stale_browsers():
    """采集前清理残留的 browser-use daemon 进程,避免资源臃肿"""
    try:
        # 杀掉所有 browser_use.skill_cli.daemon 进程
        subprocess.run(['pkill', '-9', '-f', 'browser_use.skill_cli.daemon'],
                      capture_output=True, timeout=5)
        # 杀掉所有 playwright 残留进程
        subprocess.run(['pkill', '-9', '-f', 'playwright'],
                      capture_output=True, timeout=5)
        print("[清理] 已清除残留 browser-use/playwright 进程")
    except Exception as e:
        print(f"[清理] 清理残留进程时出错(忽略): {e}")

# 景区关键词列表
SCENIC_SPOTS = [
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
CRAWL_URL = "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator"

async def check_and_load_cookies(context):
    """检查并加载已有Cookie"""
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print(f"已加载Cookie: {COOKIE_FILE}")
            return True
        except Exception as e:
            print(f"加载Cookie失败: {e}")
    return False

async def save_cookies(context):
    """保存Cookie到文件"""
    try:
        cookies = await context.cookies()
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"Cookie已保存: {COOKIE_FILE}")
    except Exception as e:
        print(f"保存Cookie失败: {e}")

async def login_and_get_cookies():
    """打开浏览器让用户登录,获取Cookie(窗口保持打开)"""
    from playwright.async_api import async_playwright

    PROFILE_DIR = os.path.expanduser("~/.cache/douyin_chrome_profile")
    DEBUG_PORT = 9223
    CDP_ENDPOINT_FILE = os.path.expanduser("~/.cache/douyin_chrome_profile/cdp_endpoint.txt")

    async with async_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        # 新版Playwright:user_data_dir 通过 launch_persistent_context 参数传入
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=[
                '--no-first-run',
                '--no-default-browser-check'
            ]
        )
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        print(f"正在打开 {CRAWL_URL} ...")
        await page.goto(CRAWL_URL, timeout=60000)

        print("=" * 50)
        print("请在浏览器中完成登录(如果还没登录)")
        print("登录完成后按回车继续...")
        print("(浏览器窗口会保持打开,下次采集直接复用)")
        print("=" * 50)
        input()

        # 保存Cookie
        await save_cookies(context)

        # 保存CDP endpoint(方便下次复用)
        try:
            ws_endpoint = browser.ws_endpoint
            if ws_endpoint:
                os.makedirs(os.path.dirname(CDP_ENDPOINT_FILE), exist_ok=True)
                with open(CDP_ENDPOINT_FILE, 'w') as f:
                    f.write(ws_endpoint)
                print(f"[CDP] Endpoint已保存: {ws_endpoint}")
        except Exception as e:
            print(f"[CDP] 获取endpoint失败: {e}")

        # 只关闭Page,保持Chrome窗口常开
        await page.close()
        print("[Chrome] 登录完成,Chrome窗口保持打开")

    return True

def parse_number(text):
    """从文本中解析数字"""
    # 匹配如 "85,759" 或 "4,106" 格式
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def parse_page_text(text, spot_name, all_spot_names):
    """从页面文本中解析指定景区的数据(基于区块边界解析)"""
    data = {
        "name": spot_name,
        "search": 0,
        "synth": 0,
        "trend": 0,
        "search_trend": "",
        "synth_trend": ""
    }

    if spot_name not in text:
        return data

    lines = text.split('\n')

    # 找到该景区在lines中的索引(取第一个匹配)
    spot_idx = None
    for i, line in enumerate(lines):
        if line.strip() == spot_name:
            spot_idx = i
            break
    if spot_idx is None:
        return data

    # 确定该景区区块的结束位置(下一个景区名之前)
    next_spot_idx = len(lines)
    for i in range(spot_idx + 1, len(lines)):
        for other_spot in all_spot_names:
            if lines[i].strip() == other_spot:
                next_spot_idx = i
                break
        if next_spot_idx < len(lines):
            break

    # 在区块内查找搜索指数和综合指数
    for j in range(spot_idx + 1, next_spot_idx):
        lbl = lines[j].strip()

        if lbl == "搜索指数" and data["search"] == 0:
            # 搜索指数标签后,找第一个数字(跳过"有异动")
            for k in range(j + 1, min(j + 5, next_spot_idx)):
                val = lines[k].strip()
                if val == "有异动":
                    # "有异动"时,真实数字在下一行
                    for k2 in range(k + 1, min(k + 4, next_spot_idx)):
                        v2 = lines[k2].strip()
                        n = parse_number(v2)
                        if n > 0:
                            data["search"] = n
                            break
                    break
                n = parse_number(val)
                if n > 0:
                    data["search"] = n
                    break

        if lbl == "综合指数" and data["synth"] == 0:
            # 综合指数标签后,找第一个数字(跳过"有异动")
            for k in range(j + 1, min(j + 5, next_spot_idx)):
                val = lines[k].strip()
                if val == "有异动":
                    for k2 in range(k + 1, min(k + 4, next_spot_idx)):
                        v2 = lines[k2].strip()
                        n = parse_number(v2)
                        if n > 0:
                            data["synth"] = n
                            break
                    break
                n = parse_number(val)
                if n > 0:
                    data["synth"] = n
                    break

        # 日环比:标签后跟百分比数字,通过往前回溯确定是哪个指标
        if lbl == "日环比" and j + 1 < next_spot_idx:
            trend = lines[j + 1].strip()
            if '%' in trend:
                for back in range(j - 1, max(j - 6, spot_idx), -1):
                    prev = lines[back].strip()
                    if prev == "搜索指数":
                        data["search_trend"] = trend
                        break
                    elif prev == "综合指数":
                        data["synth_trend"] = trend
                        break

    return data

async def crawl_with_cookies():
    """使用保存的Cookie采集数据

    策略:
    1. 使用固定 Chrome Profile(~/.cache/douyin_chrome_profile/)
    2. 优先通过 CDP 连接到已打开的 Chrome(窗口常开,复用登录态)
    3. 如果没有已打开的 Chrome,则启动新的
    4. 采集完成后只关闭 Page,不关闭 Browser(保持窗口常开)
    """
    from playwright.async_api import async_playwright

    today = datetime.date.today().strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "competitors": [],
        "data_url": CRAWL_URL
    }

    PROFILE_DIR = os.path.expanduser("~/.cache/douyin_chrome_profile")
    DEBUG_PORT = 9223  # 固定的调试端口,避免冲突
    CDP_ENDPOINT_FILE = os.path.expanduser("~/.cache/douyin_chrome_profile/cdp_endpoint.txt")

    async with async_playwright() as p:
        browser = None
        page = None

        # 策略1：连接 OpenClaw 浏览器（port 18800）
        try:
            print("[CDP] 尝试连接 OpenClaw Chrome: http://127.0.0.1:18800")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
            print("[CDP] OpenClaw Chrome 连接成功！")
        except Exception as e:
            print(f"[CDP] OpenClaw Chrome 连接失败: {e}")

        # 策略2：连接本地已运行的 Chrome（9222端口，专属浏览器窗口）
        if not browser:
            try:
                print("[CDP] 尝试连接本地已运行 Chrome: http://127.0.0.1:9222")
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("[CDP] 连接成功！复用已有 Chrome 窗口")
            except Exception as e:
                print(f"[CDP] 连接失败: {e}")
                browser = None

        # 策略3:无CDP连接则启动临时Chrome(使用 launch_persistent_context)
        if not browser:
            os.makedirs(PROFILE_DIR, exist_ok=True)
            print(f"[Chrome] 启动临时 Chrome(Profile: {PROFILE_DIR})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=False,
                args=[
                    '--no-first-run',
                    '--no-default-browser-check'
                ]
            )
            # 等待Chrome完全启动,获取CDP endpoint并保存
            await asyncio.sleep(2)
            try:
                # ws_endpoint 只在 Browser 对象上存在,BrowserContext 没有
                if hasattr(browser, 'ws_endpoint'):
                    ws_endpoint = browser.ws_endpoint
                    if ws_endpoint:
                        os.makedirs(os.path.dirname(CDP_ENDPOINT_FILE), exist_ok=True)
                        with open(CDP_ENDPOINT_FILE, 'w') as f:
                            f.write(ws_endpoint)
                        print(f"[CDP] 新Chrome CDP endpoint已保存: {ws_endpoint}")
                else:
                    print("[CDP] BrowserContext无ws_endpoint,跳过保存")
            except Exception as e:
                print(f"[CDP] 获取endpoint失败: {e}")

        # 创建 Page 并访问目标页面
        # connect_over_cdp 返回 Browser,launch_persistent_context 返回 BrowserContext
        if hasattr(browser, 'contexts'):
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
        else:
            # launch_persistent_context 返回 BrowserContext
            context = browser

        # 加载已有Cookie(如果存在)
        await check_and_load_cookies(context)

        page = await context.new_page()

        print(f"正在访问 {CRAWL_URL} ...")
        await page.goto(CRAWL_URL, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(3)  # 初始等待

        # 滚动页面以触发懒加载，确保所有景区数据都渲染出来
        async def scroll_to_load_all():
            last_height = 0
            scroll_attempts = 0
            max_attempts = 5
            while scroll_attempts < max_attempts:
                # 滚动到页面底部
                await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                # 检查是否已经滚到底部（没有新内容加载）
                new_height = await page.evaluate("() => document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0  # 重置，连续两次没变化才停止
                last_height = new_height
            # 滚动回顶部，确保从可见区域开始解析
            await page.evaluate("() => window.scrollTo(0, 0)")
            await asyncio.sleep(1)

        await scroll_to_load_all()

        # 检查数据日期：如果显示的是昨天/更早的日期，则强制刷新页面
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        page_text_check = await page.evaluate("() => document.body.innerText")
        if "数据日期" in page_text_check:
            # 提取页面上的数据日期
            import re
            date_match = re.search(r"数据日期[：:]\s*(\d{4}-\d{2}-\d{2})", page_text_check)
            if date_match:
                page_date = date_match.group(1)
                print(f"[刷新检查] 页面数据日期: {page_date}，今天日期: {today_str}")
                if page_date != today_str:
                    print(f"[刷新] 数据非今日({page_date} ≠ {today_str})，正在刷新页面...")
                    await page.reload(timeout=15000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    await asyncio.sleep(3)
                    await scroll_to_load_all()
                    print(f"[刷新] 页面已刷新，等待数据加载完成")

        # 获取页面文本内容(使用JavaScript获取完整文本,inner_text可能截断)
        try:
            page_text = await page.evaluate("() => document.body.innerText")
        except:
            page_text = await page.inner_text('body')
        print(f"[DEBUG] 页面文本长度: {len(page_text)}")

        print("开始解析页面数据...")

        for spot in SCENIC_SPOTS:
            spot_data = parse_page_text(page_text, spot, SCENIC_SPOTS)
            if spot_data["search"] > 0 or spot_data["synth"] > 0:
                result["competitors"].append(spot_data)
                print(f"  {spot}: 搜索={spot_data['search']}, 综合={spot_data['synth']}")
            else:
                print(f"  {spot}: 未找到数据")

        # 数据完整性校验：确保8个景区全部抓到
        if len(result["competitors"]) < 8:
            missing = [s for s in SCENIC_SPOTS if s not in [c["name"] for c in result["competitors"]]]
            print(f"[警告] 数据不完整！缺失 {len(result['competitors'])}/8 个景区: {missing}")
            result["incomplete"] = True
            result["missing_spots"] = missing
        else:
            print(f"[完成] 8/8 景区数据完整")

        # 关闭 Page(保持 Chrome 窗口常开)
        await page.close()
        print("[Chrome] Page已关闭,Chrome窗口保持打开(复用登录态)")

    return result

def get_latest_historical_data():
    """获取最新的历史数据"""
    files = glob.glob("/tmp/crawl_data_*.json")
    files = [f for f in files if "_backup" not in f]
    if not files:
        return None
    latest = max(files)
    try:
        with open(latest, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"使用历史数据: {latest}")
        return data
    except:
        return None

def save_data(data, filepath="/tmp/crawl_data.json"):
    """保存数据到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {filepath}")

def main():
    print("=" * 50)
    print("抖音指数数据采集 v9")
    print(f"数据来源: {CRAWL_URL}")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        # 登录模式
        print("登录模式:打开浏览器让用户登录")
        asyncio.run(login_and_get_cookies())
        print("登录完成!")
        return

    # 采集模式
    try:
        result = asyncio.run(crawl_with_cookies())

        # 检查是否有有效数据
        has_data = len(result.get("competitors", [])) > 0

        if not has_data:
            print("采集数据为空,使用备用方案...")
            fallback = get_latest_historical_data()
            if fallback:
                result = fallback
                result["note"] = "采集失败,使用历史数据"
            else:
                result = {
                    "date": datetime.date.today().strftime("%Y-%m-%d"),
                    "crawled_at": datetime.datetime.now().isoformat(),
                    "note": "采集失败且无历史数据",
                    "competitors": []
                }

    except Exception as e:
        print(f"采集失败: {e}")
        import traceback
        traceback.print_exc()
        fallback = get_latest_historical_data()
        if fallback:
            fallback["note"] = f"采集失败({e}),使用历史数据"
            result = fallback
        else:
            result = {
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "crawled_at": datetime.datetime.now().isoformat(),
                "note": f"采集失败: {e}",
                "competitors": []
            }

    save_data(result)
    print("采集完成!")
    return result

if __name__ == "__main__":
    main()
