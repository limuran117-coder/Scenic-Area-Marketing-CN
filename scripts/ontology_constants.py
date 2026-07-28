"""
Ontology 共享常量模块

提取 adapter-*.py 中重复定义的常量，单一事实来源。
所有 adapter 和 store 统一引用此模块。

版本: 1.0.0
创建: 2026-06-02 (Day 4)
"""

from __future__ import annotations
from pathlib import Path

# ─── 景区名称 → 语义化 ID 映射 ──────────────────

# 支持核心名称 + 常见别名（对接不同数据源的命名差异）
SCENIC_SPOT_MAP: dict[str, str] = {
    # === 核心景区 ===
    "建业电影小镇": "movie_town",
    "万岁山武侠城": "wansui_mountain",
    "清明上河园": "qingming_riverside",
    "只有河南": "only_henan",
    "只有河南戏剧幻城": "only_henan",
    "只有河南·戏剧幻城": "only_henan",
    "郑州方特欢乐世界": "fangte",
    "方特欢乐世界": "fangte",
    "郑州海昌海洋公园": "haichang",
    "海昌海洋公园": "haichang",  # 别名（小红书关键词无"郑州"前缀）D-018
    "郑州银基动物王国": "yinji",
    "银基动物王国": "yinji",  # 别名（部分数据源用此简称）D-018
    "只有红楼梦戏剧幻城": "only_dream",
    "只有红楼梦": "only_dream",  # 别名（小搜搜索常用简称）D-018
}

# 反向映射（ID → 标准名称）
SCENIC_SPOT_REVERSE: dict[str, str] = {
    "movie_town": "建业电影小镇",
    "wansui_mountain": "万岁山武侠城",
    "qingming_riverside": "清明上河园",
    "only_henan": "只有河南戏剧幻城",
    "fangte": "郑州方特欢乐世界",
    "haichang": "郑州海昌海洋公园",
    "yinji": "郑州银基动物王国",
    "only_dream": "只有红楼梦戏剧幻城",
}

# 景区级别
SCENIC_TIER: dict[str, str] = {
    "movie_town": "secondary",
    "wansui_mountain": "national",
    "qingming_riverside": "national",
    "only_henan": "secondary",
    "fangte": "secondary",
    "haichang": "secondary",
    "yinji": "secondary",
    "only_dream": "national",
}

# ─── 数据源置信度 ────────────────────────────────

CONFIDENCE_BY_SOURCE: dict[str, float] = {
    "douyin": 0.9,           # 抖音指数 — 官方数据订阅
    "xiaohongshu": 0.3,      # 小红书 — 搜索量估算（需爬虫升级）
    "internal_csv": 1.0,     # 内部 CSV — 权威数据
    "csv": 1.0,              # 同上别名
    "manual": 0.95,          # 人工录入
    "baidu": 0.6,            # 百度指数 — 公开数据 [FROZEN 2026-06-27 D-027: adapter 归档到 scripts/archive/, 5 天 spike 失败后冻结]
    "weibo": 0.5,            # 微博热搜 — 公开数据
}

# ─── 指标类型枚举 ────────────────────────────────

METRIC_TYPES: dict[str, str] = {
    "search_index": "搜索指数",
    "composite_index": "综合指数",
    "visitor_count": "客流量",
    "visitors": "门票人数",
    "revenue": "门票收入",
    "content_count": "内容数量",
    "engagement_rate": "互动率",
    "note_count": "笔记数",
}

# ─── 数据源枚举 ──────────────────────────────────

SOURCE_TYPES: dict[str, str] = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "weibo": "微博",
    "baidu": "百度",  # [FROZEN 2026-06-27 D-027]
    "internal_csv": "内部系统",
}

# ─── 工具函数 ────────────────────────────────────


def resolve_spot_id(name: str) -> str:
    """景区名称 → 语义化ID，未匹配时生成 fallback"""
    return SCENIC_SPOT_MAP.get(name, name.lower().replace(" ", "_"))


def resolve_spot_name(spot_id: str) -> str:
    """语义化ID → 标准名称，未匹配时返回原值"""
    return SCENIC_SPOT_REVERSE.get(spot_id, spot_id)


def get_confidence(source: str) -> float:
    """获取数据源置信度，未匹配时返回 0.5"""
    return CONFIDENCE_BY_SOURCE.get(source, 0.5)


def safe_float(val: str | float | None) -> float | None:
    """安全转 float，空值/非数字返回 None"""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    val = val.strip().replace(",", "")
    if not val:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# ─── 文件路径 ────────────────────────────────────

ONTOLOGY_DIR = Path(__file__).parent.parent / "wiki" / "技术配置" / "Ontology架构设计"
ONTOLOGY_JSON = ONTOLOGY_DIR / "ontology.json"
DATA_DIR = ONTOLOGY_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = Path.home() / ".profile" / "ontology" / "ontology_store.db"

# ─── 工具：日期解析 ──────────────────────────────

MONTH_MAP: dict[str, str] = {
    "1月": "01", "2月": "02", "3月": "03", "4月": "04",
    "5月": "05", "6月": "06", "7月": "07", "8月": "08",
    "9月": "09", "10月": "10", "11月": "11", "12月": "12",
}


if __name__ == "__main__":
    # 自检
    print(f"SCENIC_SPOT_MAP: {len(SCENIC_SPOT_MAP)} entries")
    print(f"CONFIDENCE_BY_SOURCE: {len(CONFIDENCE_BY_SOURCE)} entries")
    print(f"spot '建业电影小镇' → {resolve_spot_id('建业电影小镇')}")
    print(f"id 'movie_town' → {resolve_spot_name('movie_town')}")
    print(f"confidence('douyin') = {get_confidence('douyin')}")
    print(f"DB_PATH: {DB_PATH}")

# ─── 实体类型枚举（D-058 补充）────────────────────
# 对应 ontology_store.py ScenicSpot / MetricSnapshot / ContentAsset / Event 对象

ENTITY_TYPES = {
    "scenic_spot": "景区（核心实体）",
    "metric_snapshot": "指标快照",
    "content_asset": "内容资产",
    "event": "事件",
    "competitor": "竞品景区",  # [D-058] 兼容旧 adapter 硬编码
}

# ─── 关系类型枚举（D-058 补充）────────────────────
# 对应 ontology_store.py object_links 表 relation_type 列

RELATIONSHIP_TYPES = {
    "nearby": "邻近关系",
    "similar_to": "相似竞品",
    "belongs_to": "归属关系",
    "derives_from": "衍生来源",
    "competes_with": "竞争关系",
    "partners_with": "合作联动",
}

# ─── 状态枚举（D-058 补充）────────────────────────
# 通用对象状态 + 数据采集状态

STATUS_ONTOLOGY = {
    "active": "活跃",
    "inactive": "非活跃",
    "archived": "已归档",
}

STATUS_COLLECTION = {
    "pending": "待采集",
    "crawling": "采集中",
    "crawled": "已采集",
    "failed": "采集失败",
}

STATUS_QUALITY = {
    "verified": "已验证",
    "unverified": "未验证",
    "stale": "数据过期",
}
