#!/usr/bin/env python3
"""
行业热点采集脚本 v5（文章正文版）
核心：访问不需要登录的旅游媒体，直接提取文章正文

流程：
  1. Playwright+CDP访问旅游媒体列表页
  2. 提取文章URL（新浪/搜狐/网易/凤凰）
  3. 逐篇访问提取正文摘要
  4. 自动生成对电影小镇的影响判断
  5. 按SOP格式整理 → /tmp/industry_news_full.json
"""

import json
import datetime
import asyncio
import re
from playwright.async_api import async_playwright

# ─── 配置 ─────────────────────────────────────────
CDP_ENDPOINT = "http://127.0.0.1:18800"
OUTPUT_FILE = "/tmp/industry_news_full.json"
MAX_ARTICLES = 8

# 不需要登录的旅游媒体
SOURCE_PAGES = [
    ("新浪旅游", "https://travel.sina.com.cn/"),
    ("搜狐旅游", "https://travel.sohu.com/"),
]

文旅_KW = [
    "旅游", "文旅", "景区", "游客", "酒店", "OTA",
    "文旅部", "主题公园", "乐园", "文化", "演艺",
    "抖音", "小红书", "营销", "客流", "五一", "端午",
    "沉浸", "演出", "夜游", "打卡", "爆款", "网红",
    "度假", "旅行", "目的地", "游乐园", "旅行团",
]

# ─── 工具 ─────────────────────────────────────────
def clean_text(text):
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text)).strip()
    return text

def is_relevant(title):
    text = title.lower()
    return any(kw in text for kw in 文旅_KW)

async def extract_article_urls(page, url, source):
    """从列表页提取文章URL"""
    articles = []
    try:
        await page.goto(url, timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        links = await page.query_selector_all("a")
        seen = set()
        for link in links:
            try:
                href = await link.get_attribute("href") or ""
                title = (await link.inner_text() or "").strip()
                if len(title) > 8 and is_relevant(title):
                    full_url = href
                    if href.startswith("/"):
                        if "sina" in url:
                            full_url = "https://travel.sina.com.cn" + href
                        elif "sohu" in url:
                            full_url = "https://travel.sohu.com" + href
                    if full_url.startswith("http") and full_url not in seen:
                        seen.add(full_url)
                        articles.append({"title": title, "url": full_url, "source": source})
            except:
                pass
    except Exception as e:
        print(f"  [警告] {source} 列表页失败: {e}", flush=True)
    return articles[:15]

async def fetch_article(page, article):
    """访问文章页，提取正文摘要"""
    try:
        await page.goto(article["url"], timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        text = await page.evaluate('document.body.innerText')
        text = clean_text(text)

        # 去除开头的导航/订阅/广告等干扰内容
        for sep in ["打开APP", "下载客户端", "扫描二维码", "相关推荐",
                     "相关阅读", "热门内容", "我来说两句", "独家", "来源："]:
            if sep in text[:200]:
                text = text[text.index(sep)+len(sep):]

        # 提取段落
        paras = [p.strip() for p in text.split('\n') if len(p.strip()) > 40]
        if paras:
            # 找第一段有意义的内容
            for p in paras:
                if len(p) > 50 and not p.startswith(("订阅", "版权", "声明", "相关", "热门", "导航")):
                    return p[:400] + ("..." if len(p) > 400 else "")
            return paras[0][:400] + ("..." if len(paras[0]) > 400 else "")
        return text[:300] if text else "[正文获取失败]"
    except Exception as e:
        return f"[访问失败: {e}]"

def generate_analysis(title, content):
    """生成对电影小镇的影响判断"""
    text = (title + " " + content).lower()
    if any(kw in text for kw in ["ai", "人工智能", "智能"]):
        return "AI技术改变内容生产，电影小镇可探索AI短视频/互动体验，降低营销成本"
    if any(kw in text for kw in ["五一", "端午", "暑假", "国庆", "假期", "节假日", "春季", "夏季"]):
        return "节庆节点，提前2周启动预热，规划专题活动抢流量"
    if any(kw in text for kw in ["沉浸", "演出", "演艺", "剧场", "情景剧"]):
        return "沉浸式演艺是核心竞争力，电影小镇可结合热点做二次传播"
    if any(kw in text for kw in ["小红书", "抖音", "打卡", "爆款", "种草", "短视频"]):
        return "内容平台是主要获客渠道，加强KOC合作，提升UGC产出"
    if any(kw in text for kw in ["客流", "人次", "入园", "接待", "游客量"]):
        return "客流直接影响营收，持续监控并与竞品对比，适时调整营销"
    if any(kw in text for kw in ["政策", "文旅部", "补贴", "扶持", "资金", "文旅局"]):
        return "关注政策红利，主动申报夜游/文旅专项债等支持"
    if any(kw in text for kw in ["夜游", "灯光", "夜经济", "夜间"]):
        return "夜游经济是增量市场，结合电影小镇夜间场景做深度开发"
    if any(kw in text for kw in ["营销", "推广", "品牌", "活动", "策划"]):
        return "借鉴优秀营销案例，结合电影小镇调性，避免同质化"
    if any(kw in text for kw in ["竞品", "万岁山", "清明上河园", "只有河南", "方特", "银基", "海昌"]):
        return "竞品动态持续追踪，分析内容策略，取长补短"
    return "该内容与景区运营存在关联，建议结合实际参考借鉴"

# ─── 主流程 ─────────────────────────────────────────
async def main():
    print(f"📡 行业热点采集开始 ({datetime.date.today()})", flush=True)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
        page = await browser.new_page()

        print("  [1/3] 提取文章列表...", flush=True)
        all_articles = []
        for name, url in SOURCE_PAGES:
            print(f"    {name}...", end="", flush=True)
            arts = await extract_article_urls(page, url, name)
            all_articles.extend(arts)
            print(f" +{len(arts)}条", flush=True)
            await asyncio.sleep(2)

        seen = set()
        unique = []
        for a in all_articles:
            key = a["url"]
            if key not in seen:
                seen.add(key)
                unique.append(a)
        all_articles = unique
        print(f"    → 去重后共 {len(all_articles)} 篇", flush=True)

        print(f"  [2/3] 逐篇访问提取正文（最多{MAX_ARTICLES}篇）...", flush=True)
        to_visit = all_articles[:MAX_ARTICLES]
        for i, article in enumerate(to_visit):
            title_short = article["title"][:35]
            print(f"    [{i+1}/{len(to_visit)}] {title_short}...", end="", flush=True)
            content = await fetch_article(page, article)
            article["content"] = content
            article["analysis"] = generate_analysis(article["title"], content)
            print(f" ✓", flush=True)
            await asyncio.sleep(2)

        await browser.close()

    # Step3: 按SOP格式整理
    print(f"  [3/3] 按SOP格式整理...", flush=True)
    sections = format_sop(to_visit)

    result = {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "crawled_at": datetime.datetime.now().isoformat(),
        "total": len(to_visit),
        "articles": to_visit,
        "sections": sections
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！共 {len(to_visit)} 篇", flush=True)
    for sec, content in sections.items():
        lines = content.strip().split('\n')
        print(f"  【{sec}】{len(lines)}条", flush=True)

    return result

def format_sop(articles):
    """按SOP整理成4板块"""
    competitor, industry, sentiment, trend = [], [], [], []

    for a in articles:
        t = a["title"].lower()
        c = a.get("content", "")[:150]
        an = a.get("analysis", "")
        s = a.get("source", "")

        entry = f"• **{a['title']}**\n  {c}...\n  → {an}"

        if any(kw in t for kw in ["万岁山","清明上河园","只有河南","方特","银基","海昌","竞品","电影小镇"]):
            competitor.append(entry)
        elif any(kw in t for kw in ["五一","端午","沉浸","演出","打卡","爆款","网红","夜游","假期"]):
            industry.append(entry)
        elif any(kw in t for kw in ["政策","负面","投诉","舆情","风险"]):
            sentiment.append(entry)
        else:
            trend.append(entry)

    mk = lambda lst: "\n".join(lst) if lst else "• 今日暂无相关内容"

    return {
        "竞品亮点": mk(competitor[:3]),
        "泛文旅热点": mk(industry[:4]),
        "舆情提示": mk(sentiment[:2]),
        "营销趋势": mk(trend[:4]),
    }

if __name__ == "__main__":
    asyncio.run(main())
