#!/usr/bin/env python3
"""
行业热点采集脚本 v3
使用 Playwright + CDP 专属浏览器
策略：
  1. Bing搜索（对自动化友好）
  2. 36kr直接访问文章列表
  3. 环球旅讯RSS（备用）
  4. 结果存入 /tmp/industry_news.json

CDP端口: 18800
用法: python3 industry_news_browser.py
"""

import json
import datetime
import asyncio
import re
import urllib.request
import feedparser
import sys
import os
from playwright.async_api import async_playwright

# ─── 配置 ───────────────────────────────────────────
CDP_ENDPOINT = "http://127.0.0.1:18800"
OUTPUT_FILE = "/tmp/industry_news.json"
MAX_RESULTS = 20       # 最多采集条数
MAX_VISIT = 6           # 最多访问文章详情页数
SEARCH_DELAY = 3        # 搜索间隔秒数

# 搜索关键词组合
SEARCH_QUERIES = [
    "文旅行业热点 2026 五一",
    "景区营销案例 2026",
    "主题公园客流趋势 2026",
    "文旅部政策 2026",
    "沉浸式演出景区爆款",
    "旅游目的地打卡攻略",
    "文旅营销趋势报告",
]

# 文旅关键词过滤
文旅_KW = [
    "旅游", "文旅", "景区", "游客", "酒店", "OTA",
    "文旅部", "主题公园", "乐园", "文化", "演艺",
    "抖音", "小红书", "营销", "客流", "五一", "端午",
    "沉浸", "演出", "夜游", "打卡", "爆款", "网红",
    "度假", "旅行", "目的地", "游乐园", "旅行团",
]
过滤_KW = [
    "加密货币", "比特币", "美股", "战争", "明星八卦",
]

# ─── 工具函数 ────────────────────────────────────────
def clean_text(text):
    """清理HTML和多余空白"""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_relevant(title, snippet=""):
    """判断是否与文旅相关"""
    text = (title + " " + snippet).lower()
    for kw in 过滤_KW:
        if kw in text:
            return False
    for kw in 文旅_KW:
        if kw in text:
            return True
    return False

def save_json(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── 方法1：Bing搜索 ─────────────────────────────────
async def search_bing(page, query):
    """用Bing搜索，返回[(标题, URL, 摘要)]"""
    results = []
    try:
        encoded = query.replace(" ", "+")
        url = f"https://www.bing.com/search?q={encoded}&setlang=zh-CN&cc=CN"
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # 提取搜索结果
        result_items = await page.query_selector_all("li.b_algo h2 a, li.b_algo .b_title a")
        snippets = await page.query_selector_all("li.b_algo .b_desc")
        dates = await page.query_selector_all("li.b_algo .b_attribution cite")

        for i, item in enumerate(result_items[:10]):
            try:
                title = await item.inner_text()
                href = await item.get_attribute("href") or ""
                snippet = ""
                if i < len(snippets):
                    s = await snippets[i].inner_text()
                    snippet = clean_text(s)[:150]
                if len(title) > 8 and href.startswith("http") and is_relevant(title, snippet):
                    results.append({"title": title.strip(), "url": href, "snippet": snippet, "source": "Bing"})
            except:
                pass
    except Exception as e:
        print(f"  [警告] Bing搜索失败: {e}", flush=True)
    return results

# ─── 方法2：直接访问36kr文章列表 ──────────────────────
async def fetch_36kr(page):
    """直接抓36kr文章列表页"""
    articles = []
    try:
        await page.goto("https://36kr.com/information/travel/", timeout=20000, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        # 提取文章链接+标题
        items = await page.query_selector_all(".article-item a, .kr-shadow-card a, .feed-item a")
        for item in items[:15]:
            try:
                title = await item.inner_text()
                href = await item.get_attribute("href") or ""
                if "/p/" in (href or "") and len(title) > 8 and is_relevant(title):
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = "https://www.36kr.com" + href
                    articles.append({"title": title.strip(), "url": href, "source": "36kr"})
            except:
                pass
    except Exception as e:
        print(f"  [警告] 36kr访问失败: {e}", flush=True)
    return articles

# ─── 方法3：RSS备用 ─────────────────────────────────
def fetch_rss():
    """RSS源备用"""
    feeds = {
        "36氪": "https://36kr.com/feed",
    }
    all_items = []
    for name, url in feeds.items():
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/rss+xml, application/xml, */*"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read()
            feed = feedparser.parse(content)
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                if is_relevant(title):
                    all_items.append({
                        "title": title.strip(),
                        "url": entry.get("link", ""),
                        "source": f"RSS-{name}"
                    })
        except Exception as e:
            print(f"  [警告] {name} RSS失败: {e}", flush=True)
    return all_items

# ─── 方法4：读文章详情 ───────────────────────────────
async def visit_article(page, article):
    """访问文章页，尝试提取正文摘要"""
    try:
        await page.goto(article["url"], timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        text = await page.evaluate('document.body.innerText')
        text = clean_text(text)[:500]
        return text
    except:
        return article.get("snippet", "")

# ─── 主流程 ─────────────────────────────────────────
async def main():
    print(f"📡 行业热点采集开始 ({datetime.date.today()})", flush=True)

    # Step 1: RSS备用（不依赖浏览器，最稳定）
    print("  [1/4] RSS备用源...", flush=True)
    rss_results = fetch_rss()
    print(f"    → RSS获得 {len(rss_results)} 条", flush=True)

    all_articles = list(rss_results)

    # Step 2: 用CDP浏览器搜索Bing
    print("  [2/4] Bing搜索...", flush=True)
    bing_results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
            page = await browser.new_page()

            for query in SEARCH_QUERIES:
                print(f"    搜索: {query[:30]}...", end="", flush=True)
                results = await search_bing(page, query)
                bing_results.extend(results)
                print(f" {len(results)}条", flush=True)
                await asyncio.sleep(SEARCH_DELAY)

            # Step 3: 尝试36kr
            print("  [3/4] 36kr直接抓取...", flush=True)
            kr_results = await fetch_36kr(page)
            all_articles.extend(kr_results)
            print(f"    → 36kr获得 {len(kr_results)} 条", flush=True)

            # 把Bing结果加进来
            all_articles.extend(bing_results)

            await browser.close()
    except Exception as e:
        print(f"  [错误] 浏览器连接失败: {e}", flush=True)

    # Step 4: 去重
    print("  [4/4] 去重合并...", flush=True)
    seen = set()
    unique = []
    for a in all_articles:
        key = a["title"][:25]
        if key not in seen and is_relevant(a["title"]):
            seen.add(key)
            unique.append(a)

    result = {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "crawled_at": datetime.datetime.now().isoformat(),
        "total": len(unique),
        "articles": unique[:MAX_RESULTS]
    }

    save_json(result)

    print(f"\n✅ 完成：共 {len(unique)} 条有效数据", flush=True)
    for a in unique[:8]:
        print(f"  [{a['source']}] {a['title'][:55]}", flush=True)

    return result

if __name__ == "__main__":
    asyncio.run(main())
