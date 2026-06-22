#!/opt/homebrew/bin/python3.12
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
        ctx = browser.contexts[0]
        # 找百度页面 或 新开
        target = None
        for pg in ctx.pages:
            if pg.url and 'baidu.com' in pg.url:
                target = pg
                break
        if not target:
            target = await ctx.new_page()
        await target.goto('https://www.baidu.com/s?wd=' + '银基动物王国' + '&rn=20')
        await target.wait_for_timeout(5000)
        text = await target.evaluate('() => document.body.innerText')
        with open('/tmp/baidu_silver_text.txt', 'w') as f:
            f.write(text[:6000])
        # 标题+url
        results = await target.evaluate('''() => {
            const items = [];
            document.querySelectorAll('h3, .result-op, .c-title').forEach(el => {
                const a = el.querySelector('a') || el.closest('a');
                items.push({title: el.innerText, href: a?.href || ''});
            });
            return items.slice(0, 20);
        }''')
        print('=== 银基动物王国 百度结果 ===')
        for r in results[:20]:
            print(f'- {r["title"][:60]} | {r["href"][:60]}')
        print('已保存文本到 /tmp/baidu_silver_text.txt')

asyncio.run(main())
