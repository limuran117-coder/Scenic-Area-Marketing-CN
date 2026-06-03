#!/opt/homebrew/bin/python3.12
"""
小红书灵犀后台 keep-alive 保活脚本
通过 CDP 浏览器(端口18800)访问灵犀后台，保持 session 不超时
同时同步 Cookie 到 /tmp/xiaohongshu_cookies.json

原理：大部分 Web 平台(session)的超时机制是「无活动 X 分钟后登出」
      每 45 分钟刷新一次灵犀首页 + 同步Cookie，session 就能持续有效

用法：python3 lingxi_keepalive.py
建议：cron 每 45 分钟执行一次（07:00–22:00）
"""
import json, os, sys, time, asyncio

CDP_URL = "http://127.0.0.1:18800"
LINGXI_URL = "https://idea.xiaohongshu.com/idea/welcome/index"
COOKIE_PATH = "/tmp/xiaohongshu_cookies.json"

LOCK_PATH = "/tmp/lingxi_keepalive.lock"

async def keepalive():
    from playwright.async_api import async_playwright

    # 互斥锁 — 防止 cron 同时跑两个实例
    lock_fd = None
    try:
        lock_fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        # 检查锁是否过期（超过 60 秒的旧锁直接清除）
        age = time.time() - os.path.getmtime(LOCK_PATH)
        if age > 60:
            os.remove(LOCK_PATH)
            lock_fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL)
        else:
            print(f"[⏳] 上一个保活实例还在运行（{age:.0f}秒前启动），跳过")
            return True

    try:
        async with async_playwright() as p:
            # 连接到已有的 CDP 浏览器
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print("[✓] 已连接到 CDP 浏览器 (端口18800)")

            # 获取所有页面
            pages = browser.contexts[0].pages if browser.contexts else []
            
            # 找灵犀标签页
            target_page = None
            for page in pages:
                url = page.url
                if "idea.xiaohongshu.com" in url:
                    target_page = page
                    print(f"[✓] 找到灵犀标签页: {url[:60]}...")
                    break
            
            if not target_page:
                # 没找到 — 新建标签页
                target_page = await pages[0].context.new_page() if pages else None
                if not target_page:
                    print("[❌] 无法创建新页面")
                    return False
                print("[!] 未找到已有灵犀标签页，新建中...")

            # 激活并刷新 — 请求服务器端续期 session
            await target_page.bring_to_front()
            await target_page.goto(LINGXI_URL, wait_until="networkidle", timeout=20000)
            print("[✓] 灵犀页面已刷新，session 已续期")

            # 检查是否真的登录了（关键指标出现才算登录成功）
            try:
                await target_page.wait_for_selector(
                    "text=人群资产或text=搜索量或text=关键数据指标",
                    timeout=8000
                )
                print("[✓] 登录状态确认：关键数据已加载")
            except:
                # 不是致命错误，可能页面布局略有不同
                print("[⚠️] 未检测到关键数据指标，登录状态存疑")

            # 提取 Cookie
            cookies = await target_page.context.cookies()
            
            # 筛选小红书相关 Cookie
            xhs_cookies = [
                c for c in cookies
                if 'xiaohongshu' in c.get('domain', '') or 'idea' in c.get('domain', '')
            ]
            if not xhs_cookies:
                xhs_cookies = cookies  # 保底全部保存

            # 写入文件
            with open(COOKIE_PATH, 'w', encoding='utf-8') as f:
                json.dump(xhs_cookies, f, ensure_ascii=False, indent=2)

            print(f"[🍪] Cookie 已同步 → {COOKIE_PATH} ({len(xhs_cookies)}条)")

            # 检查是否有 session/token 类 Cookie
            has_session = any(
                'session' in c.get('name', '').lower() or 
                'token' in c.get('name', '').lower() or
                'sid' in c.get('name', '').lower()
                for c in xhs_cookies
            )
            if not has_session:
                print("[⚠️] 警告：未检测到 session/token Cookie，可能已登出")

            # 关闭新建的标签页（如果是新建的）
            if target_page.url != LINGXI_URL:
                # 如果是新建页面且不在正常页面上，关闭它
                pass

            print("[✅] 保活完成")
            return True

    except Exception as e:
        print(f"[❌] 保活异常: {e}")
        return False
    finally:
        # 释放锁
        if lock_fd is not None:
            try:
                os.close(lock_fd)
                os.remove(LOCK_PATH)
            except:
                pass

if __name__ == "__main__":
    ts = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    print(f"=== 灵犀保活 [{ts}] ===")
    ok = asyncio.run(keepalive())
    sys.exit(0 if ok else 1)
