#!/opt/homebrew/bin/python3.12
"""
小红书日报数据采集器 v2
- 不依赖 LLM，纯 Playwright 编排
- 用 search_result URL（避开新版 explore 页的"点点 AI" div 干扰）
- 8 景区一次性采完
- 输出 /tmp/xhs_daily_data.json
- 设计：采集层与 LLM 解耦，M3 撞限也不丢数据

v2 修复 (2026-06-10)：
- 探针证实 explore 页搜索框被"问点点 AI"取代，4 个 selector 全失效
- search_result URL + 等 4 秒 + 滚 1 次 + 5s/关键词间隔 = 稳定
- 文本解析提取 note 链接 + 笔记标题
"""
import json
import datetime
import asyncio
import sys
from playwright.async_api import async_playwright

CDP_HOST = "http://127.0.0.1"
DEFAULT_CDP_PORT = 18800

KEYWORDS = [
    "建业电影小镇",
    "只有河南",
    "银基动物王国",
    "万岁山武侠城",
    "清明上河园",
    "方特欢乐世界",
    "海昌海洋公园",
    "只有红楼梦戏剧幻城",
]

OUTPUT_FILE = "/tmp/xhs_daily_data.json"

LINGXI_URL = "https://edith.xiaohongshu.com/idea/welcome/index"
LINGXI_KEYWORDS = ["建业电影小镇"]  # 灵犀仅查本品牌
LINGXI_FALLBACK_INDICATORS = ["登录", "扫码", "二维码", "立即登录"]  # 未登录态的特征词


def url_encode(s: str) -> str:
    import urllib.parse
    return urllib.parse.quote(s)


async def crawl_one(p, keyword: str, cdp_url: str, timeout_ms: int = 20000) -> dict:
    """单关键词采集 - 走 search_result URL + 等 SPA 渲染"""
    result = {"keyword": keyword, "success": False, "error": None, "data": {
        "note_links": [], "note_titles": [], "raw_excerpt": ""
    }}
    try:
        browser = await p.chromium.connect_over_cdp(cdp_url, timeout=5000)
        target_tab = None
        for ctx in browser.contexts:
            for i, pg in enumerate(ctx.pages):
                try:
                    url = pg.url
                    if url and not url.startswith("chrome://"):
                        target_tab = pg
                        break
                except Exception:
                    continue
            if target_tab:
                break
        if not target_tab:
            for ctx in browser.contexts:
                target_tab = await ctx.new_page()
                break
        page = target_tab

        search_url = f"https://www.xiaohongshu.com/search_result?keyword={url_encode(keyword)}&source=web_explore_feed"
        await page.goto(search_url, timeout=timeout_ms, wait_until="domcontentloaded")
        # SPA 渲染需要等（之前 sleep 3s 失败，4s+ 成功）
        await asyncio.sleep(5)
        # 滚一下触发懒加载
        await page.evaluate("window.scrollBy(0, 600)")
        await asyncio.sleep(2)

        # 提取笔记链接（带 xsec_token 的才是真笔记）
        note_links = await page.evaluate("""
() => {
    const seen = new Set();
    const out = [];
    document.querySelectorAll('a[href*="/search_result/"]').forEach(a => {
        const h = a.href;
        if (h && !seen.has(h)) {
            seen.add(h);
            out.push(h);
        }
    });
    return out.slice(0, 10);
}
""")
        # 提取笔记标题（链接周围的文本）
        note_titles = await page.evaluate("""
() => {
    const out = [];
    document.querySelectorAll('a[href*="/search_result/"]').forEach(a => {
        const t = (a.innerText || '').trim();
        if (t && t.length > 3 && t.length < 100) {
            out.push(t);
        }
    });
    return [...new Set(out)].slice(0, 10);
}
""")
        text = await page.inner_text("body")
        result["data"] = {
            "note_links": note_links,
            "note_titles": note_titles,
            "raw_excerpt": text[:600],
            "hit_count": text.count(keyword[:2])  # 用关键词前 2 字评估命中
        }
        result["success"] = len(note_links) > 0
        if not result["success"]:
            result["error"] = "no_note_links"
        await browser.close()
    except Exception as e:
        result["error"] = str(e)[:120]
    return result


async def try_crawl_lingxi(cdp_url: str, timeout_ms: int = 20000) -> dict:
    """灵犀后台采集（降级处理）
    - 已登录：提取人群资产 / 搜索量 / 阅读渗透率 / 关联词 / SOV
    - 未登录：返回 success=False, error='not_logged_in'，调用方需在卡片中说明
    """
    result = {"success": False, "error": None, "data": {}, "note": ""}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(cdp_url, timeout=5000)
            target_tab = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    try:
                        if "xiaohongshu.com" in (pg.url or ""):
                            target_tab = pg
                            break
                    except Exception:
                        continue
                if target_tab:
                    break
            if not target_tab:
                for ctx in browser.contexts:
                    target_tab = await ctx.new_page()
                    break
            page = target_tab
            await page.goto(LINGXI_URL, wait_until="domcontentloaded", timeout=timeout_ms)
            await asyncio.sleep(6)
            text = await page.inner_text("body")
            # 登录态检测
            not_logged = any(ind in text for ind in LINGXI_FALLBACK_INDICATORS) or len(text) < 200
            if not_logged:
                result["error"] = "not_logged_in"
                result["note"] = "灵犀后台需重新登录。访问 https://edith.xiaohongshu.com 扫码登录一次即可恢复。"
                await browser.close()
                return result
            # 已登录：提取五维指标（探针阶段拿不准字段名，先存原始文本等LLM解读）
            metrics = await page.evaluate("""
() => {
    const t = document.body.innerText;
    const grab = (re) => {
        const m = t.match(re);
        return m ? m[0] : null;
    };
    return {
        crowd_assets: grab(/人群资产[^0-9]*([\\d,\\.亿]+)/),
        search_volume: grab(/搜索量[^0-9]*([\\d,\\.亿]+)/),
        read_rate: grab(/阅读渗透率[^\\d]*([\\-\\d\\.]+%)/),
        click_index: grab(/点击指数[^0-9]*([\\d,\\.亿]+)/),
        raw_excerpt: t.slice(0, 800)
    };
}
""")
            result["success"] = True
            result["data"] = metrics
            await browser.close()
    except Exception as e:
        result["error"] = str(e)[:120]
    return result


async def main():
    cdp_port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CDP_PORT
    cdp_url = f"{CDP_HOST}:{cdp_port}"
    started = datetime.datetime.now().isoformat()

    # CDP 健康检查
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(cdp_url, timeout=5000)
            await browser.close()
    except Exception as e:
        print(f"✗ CDP 连接失败: {e}", flush=True)
        sys.exit(1)

    print(f"小红书日报采集 v2 | {len(KEYWORDS)} 关键词 | {started}", flush=True)
    results = []
    async with async_playwright() as p:
        for kw in KEYWORDS:
            print(f"  → {kw}", flush=True)
            r = await crawl_one(p, kw, cdp_url)
            results.append(r)
            status = "✓" if r["success"] else "✗"
            err = f" ({r['error']})" if r["error"] else ""
            n = len(r["data"].get("note_links", [])) if r["data"] else 0
            print(f"    {status}{err} | {n} 笔记链接", flush=True)
            await asyncio.sleep(3)  # 关键词间隔

    finished = datetime.datetime.now().isoformat()
    # 灵犀后台（可选，降级）
    lingxi = await try_crawl_lingxi(cdp_url)
    if lingxi["success"]:
        print(f"\n✓ 灵犀后台已采集: 人群资产={lingxi['data'].get('crowd_assets','-')} 搜索量={lingxi['data'].get('search_volume','-')}", flush=True)
    else:
        print(f"\n⚠️ 灵犀后台跳过: {lingxi['error']}", flush=True)

    out = {
        "started_at": started,
        "finished_at": finished,
        "version": "v3-search_result+lingxi-degrade",
        "keyword_count": len(KEYWORDS),
        "success_count": sum(1 for r in results if r["success"]),
        "results": results,
        "lingxi": lingxi,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n完成 {out['success_count']}/{out['keyword_count']}", flush=True)
    print(f"输出: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
