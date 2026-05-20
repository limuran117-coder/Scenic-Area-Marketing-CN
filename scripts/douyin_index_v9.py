#!/usr/bin/env python3
"""
抖音指数数据采集脚本 v10
使用Playwright浏览器自动化采集抖音创作者平台指数数据
支持Cookie持久化登录态，增强反爬抵御能力

变更记录:
v10 - 2026-05-16
  - URL更新: https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
  - 增加Cookie预检机制，采集前先验证登录态
  - 所有操作间隔调大到5-8秒+随机抖动(-30%~+30%)
  - 增加人类行为模拟(鼠标随机移动)
  - Cookie过期时生成错误标记，避免静默失败

数据订阅页面(包含已订阅景区概览):
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
import fcntl
import time
import random
import subprocess


# ========================
# 反爬策略工具函数
# ========================

def random_jitter(base_seconds, jitter_ratio=0.3):
    """生成带随机抖动的时间(秒)，模拟人类操作的不规则节奏
    
    例如: random_jitter(6, 0.3) => 4.2 ~ 7.8 秒
    """
    delta = base_seconds * jitter_ratio
    return base_seconds - delta + random.random() * 2 * delta


async def human_sleep(base_seconds, jitter_ratio=0.3):
    """sleep with random jitter，模拟人类操作间隔"""
    duration = random_jitter(base_seconds, jitter_ratio)
    await asyncio.sleep(duration)


async def human_mouse_move(page):
    """模拟人类鼠标随机小幅度移动，降低自动化检测概率"""
    try:
        viewport = page.viewport_size or {"width": 1440, "height": 900}
        for _ in range(random.randint(1, 3)):
            x = random.randint(100, viewport.get("width", 1440) - 100)
            y = random.randint(100, viewport.get("height", 900) - 100)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.3, 1.0))
    except Exception:
        pass  # 模拟移动失败不影响主流程


async def check_login_status(page):
    """检查抖音登录态是否有效
    
    策略：访问轻量页面，检查是否被重定向到登录页/验证页。
    Returns: True=已登录 | False=Cookie过期
    """
    try:
        check_url = "https://creator.douyin.com/creator-micro/home"
        await page.goto(check_url, timeout=20000, wait_until="domcontentloaded")
        await asyncio.sleep(random_jitter(3, 0.3))
        
        current_url = page.url
        page_text = await page.evaluate("() => document.body.innerText")
        
        # 检查是否被重定向到登录页
        if any(hint in current_url for hint in ["passport", "login", "account"]):
            print("[Cookie预检] ✗ 被重定向到登录页，Cookie已过期")
            return False
        
        # 检查页面文本中是否有登录相关关键词
        login_indicators = ["请登录", "扫码登录", "手机号登录/注册", "登录抖音"]
        for indicator in login_indicators:
            if indicator in page_text:
                print(f"[Cookie预检] ✗ 页面包含'{indicator}'，Cookie已过期")
                return False
        
        print("[Cookie预检] ✓ 登录态有效")
        return True
        
    except Exception as e:
        print(f"[Cookie预检] ⚠ 检测失败({e})，按已登录继续...")
        return True  # 检测失败时保守处理，让主流程继续


def set_cookie_expired_flag():
    """写入Cookie过期标记文件，供其他脚本/任务检查"""
    flag_path = "/tmp/douyin_cookie_expired.flag"
    with open(flag_path, "w") as f:
        f.write(f"Cookie过期于: {datetime.datetime.now().isoformat()}\n")
        f.write(f"需站长重新登录抖音创作者平台\n")
    print(f"[⚠ Cookie过期] 标记文件已写入: {flag_path}")


def clear_cookie_expired_flag():
    """清除Cookie过期标记"""
    flag_path = "/tmp/douyin_cookie_expired.flag"
    if os.path.exists(flag_path):
        os.remove(flag_path)


def is_cookie_expired():
    """检查Cookie过期标记是否存在"""
    return os.path.exists("/tmp/douyin_cookie_expired.flag")


def acquire_browser_lock(lock_path="/tmp/playwright_cdp.lock", timeout=120):
    """获取浏览器独占锁，防止多脚本并发启动新窗口。
    
    流程:
    1. 尝试创建锁文件并加锁（F_SETLKW 阻塞等待）
    2. 若锁已存在且文件超过timeout秒未更新，视为过期，强制删除后重试
    3. 返回锁文件对象，调用方用完后必须 release_browser_lock()
    
    Returns: (lock_file_obj, is_fallback) 其中 is_fallback=True 表示需要启动新窗口
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            os.makedirs(os.path.dirname(lock_path), exist_ok=True)
            lock_file = open(lock_path, 'w')
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file.write(f"{os.getpid()}\n")
            lock_file.flush()
            return lock_file, False
        except (IOError, OSError):
            try:
                stat = os.stat(lock_path)
                if time.time() - stat.st_mtime > timeout:
                    print(f"[Lock] 检测到过期锁文件，强制删除后重试...")
                    os.remove(lock_path)
                    continue
            except FileNotFoundError:
                continue
            print(f"[Lock] 锁被占用，等待 8 秒后重试 CDP...")
            time.sleep(8)
    return None, True


def release_browser_lock(lock_file):
    """释放浏览器独占锁"""
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
    except Exception:
        pass


def cleanup_stale_browsers():
    """采集前清理残留的 browser-use daemon 进程,避免资源臃肿"""
    try:
        subprocess.run(['pkill', '-9', '-f', 'browser_use.skill_cli.daemon'],
                      capture_output=True, timeout=5)
        subprocess.run(['pkill', '-9', '-f', 'playwright'],
                      capture_output=True, timeout=5)
        print("[清理] 已清除残留 browser-use/playwright 进程")
    except Exception as e:
        print(f"[清理] 清理残留进程时出错(忽略): {e}")


# ========================
# 核心配置
# ========================

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
# v10: URL更新到抖音指数核心页
CRAWL_URL = "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index"

# ========================
# Cookie 管理
# ========================

async def check_and_load_cookies(context):
    """检查并加载已有Cookie（优先从SQLite数据库读取，备选JSON文件）"""
    import sqlite3
    
    sqlite_db = os.path.expanduser("~/.openclaw/chrome-profile-18800/Default/Cookies")
    if os.path.exists(sqlite_db):
        try:
            conn = sqlite3.connect(sqlite_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value, host_key, path, expires_utc, is_secure FROM cookies WHERE host_key LIKE '%douyin.com%' OR host_key LIKE '%bytedance.com%'")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                cookies_for_playwright = []
                for row in rows:
                    name, value, host_key, path, expires_utc, is_secure = row
                    cookies_for_playwright.append({
                        'name': name,
                        'value': value,
                        'domain': host_key,
                        'path': path or '/',
                        'expires': expires_utc // 1000000 - 11644473600 if expires_utc else -1,
                        'httpOnly': False,
                        'secure': bool(is_secure),
                        'sameParty': False,
                        'sourceScheme': 'Secure' if is_secure else 'NonSecure',
                        'sourcePort': 443 if is_secure else 80
                    })
                await context.add_cookies(cookies_for_playwright)
                print(f"[Cookie] 从SQLite数据库加载{len(cookies_for_playwright)}个抖音Cookie")
                return True
        except Exception as e:
            print(f"[Cookie] SQLite读取失败: {e}，尝试JSON文件")
    
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

    PROFILE_DIR = os.path.expanduser("~/.openclaw/chrome-profile-18800")

    async with async_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=['--no-first-run', '--no-default-browser-check']
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

        await save_cookies(context)
        clear_cookie_expired_flag()  # 登录成功后清除过期标记
        await page.close()
        print("[Chrome] 登录完成,Chrome窗口保持打开")

    return True


# ========================
# 核心解析逻辑
# ========================

def parse_number(text):
    """从文本中解析数字"""
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

    spot_idx = None
    for i, line in enumerate(lines):
        if line.strip() == spot_name:
            spot_idx = i
            break
    if spot_idx is None:
        return data

    next_spot_idx = len(lines)
    for i in range(spot_idx + 1, len(lines)):
        for other_spot in all_spot_names:
            if lines[i].strip() == other_spot:
                next_spot_idx = i
                break
        if next_spot_idx < len(lines):
            break

    for j in range(spot_idx + 1, next_spot_idx):
        lbl = lines[j].strip()

        if lbl == "搜索指数" and data["search"] == 0:
            for k in range(j + 1, min(j + 5, next_spot_idx)):
                val = lines[k].strip()
                if val == "有异动":
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


# ========================
# 主采集流程
# ========================

async def crawl_with_cookies():
    """使用保存的Cookie采集数据

    策略(v10增强):
    1. Cookie预检 → 先检查登录态再采集
    2. 使用固定 Chrome Profile(~/.openclaw/chrome-profile-18800/)
    3. 优先通过 CDP 连接到已打开的 Chrome
    4. 所有操作间隔加随机抖动
    5. Cookie过期时写入标记文件供外部检查
    """
    from playwright.async_api import async_playwright

    today = datetime.date.today().strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "competitors": [],
        "data_url": CRAWL_URL,
        "cookie_expired": False
    }

    PROFILE_DIR = os.path.expanduser("~/.openclaw/chrome-profile-18800")
    CDP_ENDPOINT_FILE = os.path.expanduser("~/.openclaw/chrome-profile-18800/cdp_endpoint.txt")

    async with async_playwright() as p:
        browser = None
        page = None

        # 策略1：连接 OpenClaw 浏览器（port 18800）
        lock_file = None
        try:
            print("[CDP] 尝试连接 OpenClaw Chrome: http://127.0.0.1:18800")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
            print("[CDP] OpenClaw Chrome 连接成功！")
        except Exception as e:
            print(f"[CDP] OpenClaw Chrome 连接失败: {e}")

        if not browser:
            print("[CDP] CDP 连接不可用，争抢浏览器锁...")
            lock_file, timed_out = acquire_browser_lock()
            if timed_out or not lock_file:
                print("[Error] 等待锁超时，无法启动浏览器，退出。")
                return None
            try:
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
                print("[CDP] 锁等待期间 CDP 恢复，连接成功！")
                release_browser_lock(lock_file)
                lock_file = None
            except Exception:
                release_browser_lock(lock_file)
                lock_file = None
                os.makedirs(PROFILE_DIR, exist_ok=True)
                print(f"[Chrome] 启动独立临时 Chrome(Profile: {PROFILE_DIR})")
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=PROFILE_DIR,
                    headless=False,
                    args=['--no-first-run', '--no-default-browser-check']
                )
                await human_sleep(3)
                try:
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

        # 获取context
        is_cdp_live = False  # 是否连上了已登录的CDP浏览器
        if hasattr(browser, 'contexts'):
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            # 判断是否通过CDP连接了用户已登录的Chrome
            # CDP连上后 browser.contexts[0] 是真实Chrome的默认上下文，已有活会话
            try:
                existing_cookies = await context.cookies()
                dy_cookies = [c for c in existing_cookies if 'douyin.com' in c.get('domain','')]
                if len(dy_cookies) > 5:
                    is_cdp_live = True
                    print(f"[CDP] ✓ 检测到CDP浏览器已有{len(dy_cookies)}个抖音Cookie，跳过重载")
            except Exception:
                pass
        else:
            context = browser

        # 只有非CDP模式（自己启动的浏览器）才需要手动加载Cookie
        if not is_cdp_live:
            await check_and_load_cookies(context)

        # ---- v10新增: Cookie预检 ----
        print("\n━━━ 登录态预检 ━━━")
        precheck_page = await context.new_page()
        login_ok = await check_login_status(precheck_page)
        await precheck_page.close()

        if not login_ok:
            print("[Cookie预检] ✗ 登录态已过期，停止采集流程")
            set_cookie_expired_flag()
            result["cookie_expired"] = True
            result["note"] = "Cookie过期，需站长重新登录"
            return result
        # ---- 预检结束 ----

        page = await context.new_page()
        await human_sleep(1)

        print(f"正在访问 {CRAWL_URL} ...")
        await page.goto(CRAWL_URL, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await human_sleep(6)  # v10: 拉长初始等待

        # 滚动页面以触发懒加载
        async def scroll_to_load_all():
            last_height = 0
            scroll_attempts = 0
            max_attempts = 5
            while scroll_attempts < max_attempts:
                await human_mouse_move(page)
                await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                await human_sleep(4)  # v10: 滚动后等待更长
                new_height = await page.evaluate("() => document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = new_height
            await human_mouse_move(page)
            await page.evaluate("() => window.scrollTo(0, 0)")
            await human_sleep(3)

        await scroll_to_load_all()

        # 数据日期检查
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        page_text_check = await page.evaluate("() => document.body.innerText")
        if "数据日期" in page_text_check:
            date_match = re.search(r"数据日期[：:]\s*(\d{4}-\d{2}-\d{2})", page_text_check)
            if date_match:
                page_date = date_match.group(1)
                print(f"[刷新检查] 页面数据日期: {page_date}，今天/昨日: {today_str}/{yesterday_str}")
                if page_date != today_str and page_date != yesterday_str:
                    print(f"[刷新] 数据日期异常({page_date})，正在刷新页面...")
                    await page.reload(timeout=15000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    await human_sleep(5)
                    await scroll_to_load_all()

        # 获取页面文本
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

        # 完整性校验
        if len(result["competitors"]) < 8:
            missing = [s for s in SCENIC_SPOTS if s not in [c["name"] for c in result["competitors"]]]
            print(f"[警告] 数据不完整！缺失 {len(result['competitors'])}/8 个景区: {missing}")
            result["incomplete"] = True
            result["missing_spots"] = missing
        else:
            print(f"[完成] 8/8 景区数据完整")

        await page.close()
        print("[Chrome] Page已关闭,Chrome窗口保持打开")

        # 从CDP浏览器的活会话中提取Cookie保存，供下次CDP断连时使用
        if is_cdp_live:
            await save_cookies(context)

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
    print("抖音指数数据采集 v10")
    print(f"数据来源: {CRAWL_URL}")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        print("登录模式:打开浏览器让用户登录")
        asyncio.run(login_and_get_cookies())
        print("登录完成!")
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--cdp-sync":
        print("CDP Cookie同步模式 → 委托 cdp_cookie_hub.py（全服务统一同步）")
        hub_path = os.path.expanduser("~/.openclaw/workspace/scripts/cdp_cookie_hub.py")
        if os.path.exists(hub_path):
            ret = os.system(f"python3 {hub_path} douyin")
            if ret == 0:
                clear_cookie_expired_flag()
            sys.exit(ret >> 8)
        else:
            print(f"[❌] cdp_cookie_hub.py 不存在: {hub_path}")
            print("  ↳ 使用内置CDP同步...")
            from playwright.async_api import async_playwright
            async def sync_cookies_from_cdp():
                try:
                    async with async_playwright() as p:
                        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
                        if hasattr(browser, 'contexts') and browser.contexts:
                            context = browser.contexts[0]
                            await save_cookies(context)
                            print(f"[✅ CDP同步] Cookie已保存到 {COOKIE_FILE}")
                            clear_cookie_expired_flag()
                        else:
                            print("[❌ CDP同步] CDP浏览器无可用上下文")
                except Exception as e:
                    print(f"[❌ CDP同步] 失败: {e}")
                    sys.exit(1)
            asyncio.run(sync_cookies_from_cdp())
        return

    # 采集前检查Cookie过期标记
    if is_cookie_expired():
        print("[⚠ 跳过采集] Cookie过期标记存在，需站长重新登录后运行 --login")
        result = {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "crawled_at": datetime.datetime.now().isoformat(),
            "note": "Cookie已过期，跳过采集",
            "competitors": [],
            "cookie_expired": True
        }
        save_data(result)
        return

    try:
        result = asyncio.run(crawl_with_cookies())

        if result is None:
            print("严重错误:浏览器初始化失败")
            result = {
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "crawled_at": datetime.datetime.now().isoformat(),
                "note": "浏览器初始化失败",
                "competitors": []
            }
            save_data(result)
            return

        # Cookie过期处理——不走历史数据回退，让上游知道Cookie失效
        if result.get("cookie_expired"):
            print("[Cookie过期] 采集因Cookie过期终止，不上报历史数据")
            save_data(result)
            return

        # 采集数据为空时的降级
        has_data = len(result.get("competitors", [])) > 0
        if not has_data:
            print("采集数据为空,使用备用方案...")
            fallback = get_latest_historical_data()
            if fallback:
                # 标记为降级数据
                fallback["note"] = f"采集为空，使用{fallback.get('date','?')}历史数据"
                result = fallback
            else:
                result["note"] = "采集为空且无历史数据"

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
