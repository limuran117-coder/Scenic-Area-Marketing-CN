#!/opt/homebrew/bin/python3.12
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
        ctx = browser.contexts[0]
        # 找 xhs 页面
        target = None
        for pg in ctx.pages:
            if pg.url and 'xiaohongshu.com' in pg.url:
                target = pg
                break
        if not target:
            target = await ctx.new_page()
        await target.goto('https://www.xiaohongshu.com/search_result?keyword=' + '银基动物王国')
        await target.wait_for_timeout(6000)
        # 抓取所有可见笔记标题
        titles = await target.evaluate('''() => {
            const links = document.querySelectorAll('a[href*="/search_result"]');
            const titles = [];
            const seen = new Set();
            document.querySelectorAll('section, div, span').forEach(el => {
                const t = (el.innerText || '').trim();
                if (t && t.length > 5 && t.length < 60 && !seen.has(t)) {
                    seen.add(t);
                    titles.push(t);
                }
            });
            return titles.slice(0, 50);
        }''')
        print('=== 银基动物王国 小红书 笔记标题 ===')
        for t in titles[:30]:
            print(t)
        print('---')
        text = await target.evaluate('() => document.body.innerText')
        with open('/tmp/xhs_silver_text.txt', 'w') as f:
            f.write(text[:5000])
        print(f'已保存 {len(text)} 字到 /tmp/xhs_silver_text.txt')

asyncio.run(main())
