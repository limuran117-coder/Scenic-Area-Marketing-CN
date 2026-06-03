#!/opt/homebrew/bin/python3.12
"""
种子数据: ContentAsset 表初始化

创建代表性的内容资产条目，用于:
  1. 验证 ContentAsset Schema 的完整性
  2. 测试 MetricSnapshot ←→ ContentAsset 双向引用
  3. 为 ontology_query.py 的 cross_source_correlation 提供内容维度数据

种子数据来源: 代表性的热门内容（手工录入，待爬虫升级后替换为实时数据）

运行:
  python3 seed_content_assets.py
"""

from __future__ import annotations
import json
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ontology_store import OntologyStore

# ─── 种子数据（ontology object 格式） ──────────────────

SEED_ASSETS = [
    # ── 建业电影小镇 ──
    {
        "schema": "ContentAsset",
        "id": "ca_mt_001",
        "platform": "xiaohongshu",
        "externalId": "xhs_note_mt_001",
        "mentions": ["movie_town"],
        "title": "郑州周末好去处！电影小镇一日游攻略",
        "description": "沉浸式民国街景、换装体验、夜场灯光秀，适合拍照打卡",
        "url": "https://www.xiaohongshu.com/explore/mt_001",
        "authorName": "旅行小王",
        "likes": 3200,
        "comments": 180,
        "shares": 450,
        "views": 28000,
        "publishDate": "2026-05-15",
        "type": "note",
        "sentiment": "positive",
        "isViral": True,
        "tags": ["电影小镇", "郑州旅游", "周末去哪", "拍照打卡", "民国风"],
    },
    {
        "schema": "ContentAsset",
        "id": "ca_mt_002",
        "platform": "douyin",
        "externalId": "dy_video_mt_001",
        "mentions": ["movie_town"],
        "title": "电影小镇夜场有多绝？一秒穿越回民国",
        "description": "灯光秀+沉浸式演出，周末人山人海",
        "url": "https://www.douyin.com/video/mt_001",
        "authorName": "郑州吃喝玩乐",
        "likes": 15000,
        "comments": 820,
        "shares": 2300,
        "views": 180000,
        "publishDate": "2026-05-20",
        "type": "video",
        "sentiment": "positive",
        "isViral": True,
        "tags": ["电影小镇", "夜场", "穿越民国", "郑州打卡"],
    },
    {
        "schema": "ContentAsset",
        "id": "ca_mt_003",
        "platform": "xiaohongshu",
        "externalId": "xhs_note_mt_003",
        "mentions": ["movie_town"],
        "title": "踩雷！电影小镇完全不值得去",
        "description": "门票贵、项目少、排队久，不如去只有河南",
        "url": "https://www.xiaohongshu.com/explore/mt_003",
        "authorName": "真实评价官",
        "likes": 450,
        "comments": 320,
        "shares": 60,
        "views": 12000,
        "publishDate": "2026-05-25",
        "type": "note",
        "sentiment": "negative",
        "isViral": False,
        "tags": ["电影小镇", "避雷", "郑州旅游"],
    },
    # ── 只有河南 ──
    {
        "schema": "ContentAsset",
        "id": "ca_oh_001",
        "platform": "xiaohongshu",
        "externalId": "xhs_note_oh_001",
        "mentions": ["only_henan"],
        "title": "只有河南太震撼了！21个剧场一天根本看不完",
        "description": "幻城剧场、李家村剧场、火车站剧场，每一个都让人泪目",
        "url": "https://www.xiaohongshu.com/explore/oh_001",
        "authorName": "文化旅行家",
        "likes": 8500,
        "comments": 620,
        "shares": 1800,
        "views": 95000,
        "publishDate": "2026-05-18",
        "type": "note",
        "sentiment": "positive",
        "isViral": True,
        "tags": ["只有河南", "戏剧幻城", "王潮歌", "文化之旅"],
    },
    # ── 万岁山武侠城 ──
    {
        "schema": "ContentAsset",
        "id": "ca_ws_001",
        "platform": "douyin",
        "externalId": "dy_video_ws_001",
        "mentions": ["wansui_mountain"],
        "title": "万岁山武侠城打铁花！太震撼了",
        "description": "非遗打铁花+武侠实景演出，性价比超高",
        "url": "https://www.douyin.com/video/ws_001",
        "authorName": "河南文旅推荐官",
        "likes": 25000,
        "comments": 1200,
        "shares": 4500,
        "views": 350000,
        "publishDate": "2026-05-22",
        "type": "video",
        "sentiment": "positive",
        "isViral": True,
        "tags": ["万岁山", "打铁花", "非遗", "武侠", "开封旅游"],
    },
    # ── 清明上河园 ──
    {
        "schema": "ContentAsset",
        "id": "ca_qm_001",
        "platform": "xiaohongshu",
        "externalId": "xhs_note_qm_001",
        "mentions": ["qingming_riverside"],
        "title": "清明上河园夜景绝美！仿佛走进宋代画卷",
        "description": "夜游+实景演出《大宋·东京梦华》，穿越千年的体验",
        "url": "https://www.xiaohongshu.com/explore/qm_001",
        "authorName": "古风爱好者",
        "likes": 6200,
        "comments": 340,
        "shares": 980,
        "views": 55000,
        "publishDate": "2026-05-28",
        "type": "note",
        "sentiment": "positive",
        "isViral": True,
        "tags": ["清明上河园", "宋代", "夜景", "开封", "古风"],
    },
    # ── 银基动物王国 ──
    {
        "schema": "ContentAsset",
        "id": "ca_yj_001",
        "platform": "douyin",
        "externalId": "dy_video_yj_001",
        "mentions": ["yinji"],
        "title": "带孩子去银基动物王国！近距离喂长颈鹿",
        "description": "亲子游首选，动物互动+游乐设施，孩子玩疯了",
        "url": "https://www.douyin.com/video/yj_001",
        "authorName": "郑州亲子游",
        "likes": 12000,
        "comments": 680,
        "shares": 2100,
        "views": 150000,
        "publishDate": "2026-06-01",
        "type": "video",
        "sentiment": "positive",
        "isViral": True,
        "tags": ["银基动物王国", "亲子游", "郑州遛娃", "长颈鹿"],
    },
    # ── 郑州方特 ──
    {
        "schema": "ContentAsset",
        "id": "ca_ft_001",
        "platform": "xiaohongshu",
        "externalId": "xhs_note_ft_001",
        "mentions": ["fangte"],
        "title": "方特欢乐世界最新攻略！这些项目必玩",
        "description": "过山车+4D影院+水上项目，刺激又好玩",
        "url": "https://www.xiaohongshu.com/explore/ft_001",
        "authorName": "游乐场达人",
        "likes": 3800,
        "comments": 210,
        "shares": 520,
        "views": 32000,
        "publishDate": "2026-05-30",
        "type": "note",
        "sentiment": "positive",
        "isViral": False,
        "tags": ["方特", "欢乐世界", "过山车", "郑州"],
    },
]


# ─── 主入口 ──────────────────────────────────────

def main():
    print(f"🌱 种子数据: {len(SEED_ASSETS)} 条 ContentAsset")

    by_platform = {}
    by_spot = {}
    for a in SEED_ASSETS:
        by_platform[a["platform"]] = by_platform.get(a["platform"], 0) + 1
        spot = a["mentions"][0] if a.get("mentions") else "?"
        by_spot[spot] = by_spot.get(spot, 0) + 1
    print(f"  按平台: {json.dumps(by_platform, ensure_ascii=False)}")
    print(f"  按景区: {json.dumps(by_spot, ensure_ascii=False)}")

    with OntologyStore() as store:
        count = store.ingest_content_assets(SEED_ASSETS, adapter_name="seed_content_assets")
    
    print(f"[DONE] 写入 ContentAsset: {count} 条")


if __name__ == "__main__":
    main()
