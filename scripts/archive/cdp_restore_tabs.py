#!/opt/homebrew/bin/python3.12
"""
CDP浏览器标签页自动恢复脚本
使用Playwright连接CDP端口18800，检查7个固定标签页是否存在，缺失则自动恢复
"""
import asyncio

CDP_PORT = 18800
TABS = [
    ("Tab0", "https://idea.xiaohongshu.com/idea/welcome/index"),
    ("Tab1", "https://www.douyin.com/search/"),
    ("Tab2", "about:blank"),
    ("Tab3", "https://www.baidu.com/s?wd="),
    ("Tab4", "https://creator.douyin.com/creator-micro/creator-count/my-subscript"),
    ("Tab5", "https://www.xiaohongshu.com/explore"),
    ("Tab6", "https://weibo.com/"),
]

async def restore():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[❌] playwright 未安装，无法连接CDP浏览器")
        return False

    try:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(f'http://127.0.0.1:{CDP_PORT}', timeout=5000)
        context = browser.contexts[0]
        existing_pages = context.pages
        
        existing_urls = []
        for pg in existing_pages:
            try:
                url = pg.url
                existing_urls.append(url.split('?')[0])
            except:
                pass
        
        print(f"当前浏览器有 {len(existing_pages)} 个标签页")
        
        restored = 0
        for label, target_url in TABS:
            target_base = target_url.split('?')[0]
            if target_base not in existing_urls:
                try:
                    new_page = await context.new_page()
                    await new_page.goto(target_url, wait_until='domcontentloaded', timeout=10000)
                    restored += 1
                    print(f"恢复: {label} -> {target_url[:50]}")
                except Exception as e:
                    print(f"恢复 {label} 失败: {e}")
        
        if restored == 0:
            print(f"全部 {len(TABS)} 个标签页正常")
        else:
            print(f"已恢复 {restored} 个标签页")
        
        await browser.close()
        await p.stop()
        return True
    except Exception as e:
        print(f"连接CDP失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(restore())
