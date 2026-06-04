#!/opt/homebrew/bin/python3.12
"""
Ontology Adapter: 百度指数 → MetricSnapshot Objects

数据源: 百度指数 (https://index.baidu.com/)
状态: PARTIAL (Day 6, 2026-06-04) — 部分景区有数据，CDP浏览器可采集

🔬 Day 6 实测结果 (2026-06-04, CDP端口18800, 账号: 李思洋912):
  | 关键词           | 状态         | 搜索指数 | 资讯指数   | 备注                     |
  |:-----------------|:-------------|:---------|:-----------|:-------------------------|
  | 清明上河园        | ✅ 有数据    | 563      | 931,584    | 同比-49%/-52%, 资讯+1196% |
  | 建业电影小镇      | ❌ 无数据    | —        | —          | 搜索量低于收录阈值         |
  | 只有河南          | ❌ 未收录    | —        | —          | 需购买创建新词权限         |
  | 万岁山武侠城      | ❌ 未收录    | —        | —          | 需购买创建新词权限         |

可行性评估 (更新):
  - CDP浏览器登录百度指数 ✅ 可行（已登录李思洋912）
  - 8景区的8个关键词中仅1个有数据（12.5%覆盖率）
  - 未收录关键词需购买百度"创建新词"权限
  - URL模式: /v2/main/index.html#/trend/{encoded}?words={encoded}
  - 搜索指数包含: 整体日均值, 移动日均值, 同比, 环比
  - 资讯指数包含: 日均值, 同比, 环比
  - 页面有: 趋势研究, 需求图谱, 人群画像 三个Tab

数据采集方案（已评估）:
  1. ❌ API 直调 — 百度指数无公开 API
  2. ✅ CDP 浏览器 — 可行！通过已登录Chrome读取页面数据
     - 方式A: snapshot提取表格数据（简单但依赖DOM结构）
     - 方式B: evaluate注入JS读取图表SVG/Canvas数据（复杂但完整）
     - 方式C: 拦截XHR请求获取API响应（最优但需逆向）
  3. ⚠️ 第三方工具 — 如 5118/SEMrush 代理采集（付费）

覆盖率限制:
  - 仅头部景区（清明上河园）有百度搜索指数
  - 中小景区需购买"创建新词"权限（付费功能）
  - 建议: adapter-baidu.py 作为可选数据源，非核心链路

字段映射设计:
  - search_index   ← 百度搜索指数（整体日均值）
  - info_index     ← 百度资讯指数（日均值）
  - composite_index ← 留空（百度无此概念）
  - audience       ← 人群画像Tab（JSON metadata）
  - region_data    ← 地域分布Tab（JSON metadata）

与 douyin 指数差异:
  | 维度       | 抖音指数              | 百度指数              |
  |:-----------|:--------------------|:---------------------|
  | 搜索范围   | 抖音站内搜索          | 全网百度搜索           |
  | 用户意图   | 娱乐/消费导向          | 信息/查询导向           |
  | 人群覆盖   | 偏年轻/女性           | 全年龄段/均衡           |
  | 竞品对比   | 支持（最多6个）        | 支持（最多5个）         |
  | 自动化难度 | 中等（代理+CDP）      | ⚠️ 中等（CDP可行但覆盖率低）|
  | 景区覆盖率 | 100%（8/8）           | ⚠️ 12.5%（1/8实测）     |

结论: adapter-baidu.py 转为 PARTIAL 状态
     - 骨架+映射设计 ✅ 完成
     - CDP采集方案 ✅ 验证可行
     - 覆盖率 ⚠️ 仅12.5%，作为可选补充数据源
     - 建议: 优先完善douyin+visitors核心链路，baidu为加分项

前置条件:
  - 百度指数账号登录状态（CDP浏览器可复用）
  - 关键词创建权限（覆盖更多景区的付费功能）
  - 数据采集脚本 (scripts/crawl_baidu.py) — 方式A优先

运行:
  python3 adapter-baidu.py [--data /path/to/baidu_data.json]
"""

from __future__ import annotations
import json
import os
import sys
import datetime
import hashlib
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ontology_store import OntologyStore
from ontology_constants import (
    SCENIC_SPOT_MAP,
    resolve_spot_id,
    resolve_spot_name,
    safe_float,
    get_confidence,
)

# ─── 常量 ────────────────────────────────────────

SOURCE = "baidu"
CONFIDENCE = 0.6  # 百度指数置信度中等（受反爬+采样影响）

# 竞品在百度指数的关键词映射（可能与抖音不同）
BAIDU_KEYWORD_MAP = {
    "movie_town": ["建业电影小镇", "电影小镇"],
    "only_henan": ["只有河南", "只有河南戏剧幻城"],
    "wansui_mountain": ["万岁山武侠城", "万岁山"],
    "qingming_riverside": ["清明上河园"],
    "fangte": ["郑州方特", "方特欢乐世界"],
    "yinji": ["银基动物王国", "郑州银基"],
    "haichang": ["海昌海洋公园", "郑州海昌"],
}

# ─── 数据解析 ────────────────────────────────────


def parse_baidu_index(data_path: str) -> list[dict]:
    """
    解析百度指数数据 → MetricSnapshot objects

    预期数据格式 (JSON):
    {
      "date": "2026-06-03",
      "crawled_at": "...",
      "source": "baidu-index",
      "keywords": {
        "建业电影小镇": {
          "search_index": 12345,
          "info_index": 890,
          "search_trend": "+5.2%",
          "region_top3": [
            {"province": "河南", "ratio": 0.35},
            {"province": "山东", "ratio": 0.12}
          ],
          "audience": {
            "age_19_24": 0.15, "age_25_34": 0.35, "age_35_44": 0.25,
            "male": 0.55, "female": 0.45
          }
        }
      }
    }
    """
    if not os.path.exists(data_path):
        print(f"[BLOCKED] 百度指数数据文件不存在: {data_path}")
        print(f"  前置条件: 需要先实现数据采集脚本 (scripts/crawl_baidu.py)")
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    objects = []
    date_str = raw.get("date", datetime.date.today().isoformat())
    keywords = raw.get("keywords", {})

    for keyword, kdata in keywords.items():
        # 反向查找 scenic_spot_id
        spot_id = _match_keyword_to_spot(keyword)
        if not spot_id:
            print(f"[WARN] 关键词 '{keyword}' 无法匹配景区")
            continue

        # 搜索指数
        search_val = safe_float(kdata.get("search_index"))
        if search_val is not None:
            obj = _build_metric(
                spot_id=spot_id,
                metric_type="search_index",
                date_str=date_str,
                value=search_val,
                metadata={
                    "keyword": keyword,
                    "daily_change": kdata.get("search_trend"),
                    "region_data": kdata.get("region_top3"),
                },
            )
            objects.append(obj)

        # 资讯指数
        info_val = safe_float(kdata.get("info_index"))
        if info_val is not None:
            obj = _build_metric(
                spot_id=spot_id,
                metric_type="info_index",
                date_str=date_str,
                value=info_val,
                metadata={
                    "keyword": keyword,
                    "audience": kdata.get("audience"),
                },
            )
            objects.append(obj)

    print(f"[OK] 百度指数解析: {len(objects)} 条 (置信度: {CONFIDENCE})")
    return objects


def _match_keyword_to_spot(keyword: str) -> str | None:
    """将百度关键词映射到景区ID"""
    for spot_id, kw_list in BAIDU_KEYWORD_MAP.items():
        for kw in kw_list:
            if kw in keyword or keyword in kw:
                return spot_id
    return None


def _build_metric(spot_id, metric_type, date_str, value, metadata=None) -> dict:
    """构建 MetricSnapshot ontology object"""
    key = f"{spot_id}|{SOURCE}|{date_str}|{metric_type}"
    obj_id = "ms_" + hashlib.md5(key.encode()).hexdigest()[:12]

    return {
        "schema": "MetricSnapshot",
        "id": obj_id,
        "scenicSpotId": spot_id,
        "source": SOURCE,
        "date": date_str,
        "metricType": metric_type,
        "value": value,
        "dailyChange": None,
        "weeklyChange": None,
        "confidence": CONFIDENCE,
        "metadata": {
            "adapter": "adapter-baidu.py",
            "collected_at": datetime.datetime.now().isoformat(),
            **(metadata or {}),
        },
    }


# ─── 写入 Ontology Store ────────────────────────


def write_to_store(objects: list[dict]) -> int:
    """写入 Ontology Store，返回写入行数"""
    if not objects:
        print("[SKIP] 无数据可写入")
        return 0
    with OntologyStore() as store:
        count = store.ingest_metric_snapshots(objects, adapter_name="baidu")
    return count


# ─── 主入口 ──────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="百度指数 → Ontology Store",
        epilog="⚠️ 当前状态: SPIKE — 数据采集前置条件未满足",
    )
    parser.add_argument("--data", default=None, help="百度指数 JSON 数据文件路径")
    args = parser.parse_args()

    if not args.data:
        print("=" * 60)
        print(" adapter-baidu.py — 百度指数 Adapter (SPIKE)")
        print("=" * 60)
        print()
        print("📊 状态: BLOCKED — 数据采集未就绪")
        print()
        print("前置条件:")
        print("  1. 百度指数账号登录 (https://index.baidu.com/)")
        print("  2. 反爬策略分析 (CAPTCHA 频率, IP 限制)")
        print("  3. 数据采集脚本 (scripts/crawl_baidu.py)")
        print()
        print("设计完成:")
        print("  ✅ 关键词→景区映射 (7个景区, 15个关键词)")
        print("  ✅ MetricSnapshot 字段映射 (search_index, info_index)")
        print("  ✅ 地域+人群画像 metadata 设计")
        print("  ✅ 竞品对比结构 (同抖音模式)")
        print()
        print("使用方法 (待采集就绪后):")
        print("  python3 adapter-baidu.py --data /tmp/baidu_index.json")
        print()
        print("参照: adapter-douyin.py (已验证通过)")
        return

    objects = parse_baidu_index(args.data)
    count = write_to_store(objects)
    print(f"[DONE] 写入 Ontology Store: {count} 条")


if __name__ == "__main__":
    main()
