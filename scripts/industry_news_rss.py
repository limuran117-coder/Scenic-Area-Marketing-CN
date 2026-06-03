#!/opt/homebrew/bin/python3.12
"""
行业热点RSS采集脚本
使用 feedparser 读取各行业媒体RSS源
稳定可靠，不依赖JS渲染

安装依赖: pip3 install feedparser
"""

import feedparser
import datetime
import json
import sys
import re
import urllib.request

# RSS源列表
RSS_FEEDS = {
    "环球旅讯": "https://www.traveldaily.cn/feed",
    "36氪科技": "https://36kr.com/feed",
    "钛媒体": "https://www.tmith.com/feed",
    "执惠": "https://www.tongjoint.com/rss/",
    "劲旅网": "http://www.tourtiger.com/rss/",
}

# 关键词过滤（只保留文旅相关内容）
文旅_KEYWORDS = [
    "旅游", "文旅", "景区", "游客", "酒店", "OTA", "航空",
    "文旅部", "目的地", "主题公园", "乐园", "文化", "演艺",
    "小红书", "抖音", "营销", "客流", "票房", "五一", "端午", "暑假", "国庆",
    "沉浸", "演出", "夜游", "打卡", "爆款", "网红", "度假", "旅行",
    "文旅局", "目的地营销", "景区运营", "主题乐园", "旅游目的地"
]

过滤_KEYWORDS = [
    "加密货币", "比特币", "股市", "美股", "A股", "期货",
    "娱乐圈", "明星八卦", "明星结婚", "选秀", "偶像",
    "战争", "政治", "体育彩票"
]

def is_relevant(title, summary=""):
    text = (title + " " + summary).lower()
    for kw in 过滤_KEYWORDS:
        if kw in text:
            return False
    for kw in 文旅_KEYWORDS:
        if kw in text:
            return True
    return False

def parse_date(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            t = datetime.datetime(*entry.published_parsed[:6])
            return t.strftime('%m-%d')
        except:
            pass
    return ""

def fetch_feed(name, url, max_items=5):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
        feed = feedparser.parse(content)
        if feed.bozo:
            return []

        items = []
        for entry in feed.entries[:max_items * 2]:
            title = entry.get('title', '') or ''
            summary = entry.get('summary', '') or ''
            summary = re.sub(r'<[^>]+>', '', summary).strip()[:200]

            if is_relevant(title, summary):
                items.append({
                    "source": name,
                    "title": title.strip(),
                    "summary": summary,
                    "date": parse_date(entry),
                    "link": entry.get('link', '')
                })
            if len(items) >= max_items:
                break
        return items
    except Exception as e:
        print(f"[警告] {name} 获取失败: {e}", file=sys.stderr)
        return []

def main():
    today = datetime.date.today().strftime('%Y-%m-%d')
    all_items = []

    print(f"📡 正在抓取行业RSS源... ({today})", file=sys.stderr)

    for name, url in RSS_FEEDS.items():
        items = fetch_feed(name, url)
        all_items.extend(items)
        print(f"  {name}: 获得 {len(items)} 条", file=sys.stderr)

    all_items.sort(key=lambda x: (x['source'], x['date']), reverse=True)

    result = {
        "date": today,
        "crawled_at": datetime.datetime.now().isoformat(),
        "total": len(all_items),
        "items": all_items
    }

    print(f"\n✅ 共 {len(all_items)} 条文旅相关资讯", file=sys.stderr)
    for item in all_items:
        print(f"  [{item['source']}] {item['title'][:60]}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
