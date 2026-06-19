"""
种子数据：DecisionRule / TouristSegment / Region
补充 ontology.json 中已定义但 db 还没填充的 Object Type
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "scripts" / "ontology"))
from ontology_store import DB_PATH  # noqa: E402


DECISION_RULES = [
    # 4 条已验证规则 (源自 BEST_PRACTICES.md §实践 4)
    {
        "id": "dr_R-001", "rule_id": "R-001",
        "name": "内容真空窗口",
        "category": "content_strategy",
        "condition": "电影小镇搜索指数连续3天 < 2000 AND 内容增量 < 5篇/天",
        "action": "启动内容创作SOP：达人合作 + UGC激励 + 站内话题运营",
        "authority_tier": 4,
        "conflict_rule": "specific_overrides_general",
        "confidence": 0.85,
        "status": "verified",
        "source": "数据驱动（2026-04-11 验证）",
        "trigger_count": 3,
    },
    {
        "id": "dr_R-002", "rule_id": "R-002",
        "name": "双节点浪费",
        "category": "timing",
        "condition": "运营/营销动作在客流低位+指数高位执行",
        "action": "调度延后到客流-指数共振窗口（高-高或低-低）",
        "authority_tier": 4,
        "conflict_rule": "higher_tier_wins",
        "confidence": 0.80,
        "status": "verified",
        "source": "数据驱动（验证2次）",
        "trigger_count": 2,
    },
    {
        "id": "dr_R-003", "rule_id": "R-003",
        "name": "竞品先动预警",
        "category": "competitive_response",
        "condition": "竞品景区抖音指数突增 > 30% (3日内)",
        "action": "启动竞品分析SOP：内容拆解 + 客流影响评估 + 应对策略",
        "authority_tier": 4,
        "conflict_rule": "specific_overrides_general",
        "confidence": 0.7,
        "status": "hypothesis",
        "source": "案例经验（待验证）",
        "trigger_count": 0,
    },
    {
        "id": "dr_R-004", "rule_id": "R-004",
        "name": "模型晚高峰规避",
        "category": "timing",
        "condition": "AI 分析/数据采集任务在 M3 配额晚高峰 (20:00-22:00) 执行",
        "action": "延后到非高峰窗口或使用本地 Python 预处理",
        "authority_tier": 5,
        "conflict_rule": "never_override",
        "confidence": 0.95,
        "status": "verified",
        "source": "Token 守则（2026-06-09 站长确认）",
        "trigger_count": 0,
    },
]

TOURIST_SEGMENTS = [
    {
        "id": "ts_亲子家庭",
        "name": "亲子家庭",
        "description": "3-12岁儿童家庭，决策者多为母亲，关注安全、教育属性",
        "age_range": "30-45",
        "gender_split": {"male": 0.3, "female": 0.7},
        "region": "郑州/开封/中牟周边",
        "characteristics": {"weekend高频": 1.0, "寒暑假高峰": 1.0, "客单价高": 0.8},
    },
    {
        "id": "ts_Z世代",
        "name": "Z世代年轻客群",
        "description": "18-28岁年轻用户，国风/汉服/二次元偏好强",
        "age_range": "18-28",
        "gender_split": {"male": 0.4, "female": 0.6},
        "region": "全国一二线城市",
        "characteristics": {"抖音小红书种草": 1.0, "打卡文化": 1.0, "客单价低": 0.6},
    },
    {
        "id": "ts_大学生",
        "name": "大学生",
        "description": "18-25岁在校学生，预算敏感，时间充裕",
        "age_range": "18-25",
        "gender_split": {"male": 0.5, "female": 0.5},
        "region": "河南/周边省份高校",
        "characteristics": {"学期周末高频": 1.0, "寒暑假回家": 0.5, "客单价低": 0.7},
    },
    {
        "id": "ts_省外游客",
        "name": "省外游客",
        "description": "中原文化体验客群，多为家庭/团体出行",
        "age_range": "25-55",
        "gender_split": {"male": 0.5, "female": 0.5},
        "region": "京津冀/长三角/珠三角",
        "characteristics": {"节假日高峰": 1.0, "客单价高": 0.9, "需住宿配套": 0.8},
    },
    {
        "id": "ts_企业团建",
        "name": "企业团建/学校研学",
        "description": "B端客群，集中性强，单次量大",
        "age_range": "20-50",
        "gender_split": {"male": 0.5, "female": 0.5},
        "region": "郑州市内",
        "characteristics": {"工作日": 1.0, "批量预订": 1.0, "高客单": 0.85},
    },
]

REGIONS = [
    {"id": "rg_河南", "name": "河南省", "level": "province", "aliases": ["豫"]},
    {"id": "rg_郑州", "name": "郑州市", "level": "city", "parent_id": "rg_河南"},
    {"id": "rg_中牟", "name": "中牟县", "level": "district", "parent_id": "rg_郑州"},
    {"id": "rg_开封", "name": "开封市", "level": "city", "parent_id": "rg_河南"},
    {"id": "rg_洛阳", "name": "洛阳市", "level": "city", "parent_id": "rg_河南"},
    {"id": "rg_北京", "name": "北京市", "level": "province", "aliases": ["京"]},
    {"id": "rg_上海", "name": "上海市", "level": "province", "aliases": ["沪"]},
    {"id": "rg_陕西", "name": "陕西省", "level": "province", "aliases": ["陕", "秦"]},
    {"id": "rg_西安", "name": "西安市", "level": "city", "parent_id": "rg_陕西"},
]

# 景区-竞品关系
SPOT_RELATIONS = [
    # 电影小镇的核心竞品
    ("movie_town", "only_henan", "competes_with", 0.95),
    ("movie_town", "qingming_riverside", "competes_with", 0.85),
    ("movie_town", "yinji_animal_kingdom", "competes_with", 0.80),
    ("movie_town", "wansuishan", "competes_with", 0.70),
    ("movie_town", "fangte_joy", "competes_with", 0.70),
    # 地理归属
    ("movie_town", "rg_中牟", "located_in", 1.0),
    ("only_henan", "rg_中牟", "located_in", 1.0),
    ("yinji_animal_kingdom", "rg_中牟", "located_in", 1.0),
    ("qingming_riverside", "rg_开封", "located_in", 1.0),
    ("wansuishan", "rg_开封", "located_in", 1.0),
]


def seed_all():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. DecisionRule
    for r in DECISION_RULES:
        cur.execute(
            """INSERT OR REPLACE INTO decision_rules
               (id, rule_id, name, category, condition, action,
                authority_tier, conflict_rule, confidence, status, source, trigger_count)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (r["id"], r["rule_id"], r["name"], r["category"], r["condition"],
             r["action"], r["authority_tier"], r["conflict_rule"], r["confidence"],
             r["status"], r["source"], r["trigger_count"]),
        )
    print(f"✅ seeded {len(DECISION_RULES)} decision_rules")

    # 2. TouristSegment
    for ts in TOURIST_SEGMENTS:
        cur.execute(
            """INSERT OR REPLACE INTO tourist_segments
               (id, name, description, age_range, gender_split, region, characteristics)
               VALUES (?,?,?,?,?,?,?)""",
            (ts["id"], ts["name"], ts["description"], ts["age_range"],
             str(ts.get("gender_split", "{}")).replace("'", '"'),
             ts.get("region", ""),
             str(ts.get("characteristics", "{}")).replace("'", '"')),
        )
    print(f"✅ seeded {len(TOURIST_SEGMENTS)} tourist_segments")

    # 3. Region（按顺序：先 province 再 city/district）
    for r in REGIONS:
        cur.execute(
            """INSERT OR IGNORE INTO regions (id, name, level, parent_id, aliases)
               VALUES (?,?,?,?,?)""",
            (r["id"], r["name"], r["level"], r.get("parent_id"),
             str(r.get("aliases", [])).replace("'", '"')),
        )
    print(f"✅ seeded {len(REGIONS)} regions")

    # 4. Spot Relations
    for src, tgt, rel, conf in SPOT_RELATIONS:
        cur.execute(
            """INSERT OR REPLACE INTO spot_relations
               (source_id, target_id, relation_type, confidence)
               VALUES (?,?,?,?)""",
            (src, tgt, rel, conf),
        )
    print(f"✅ seeded {len(SPOT_RELATIONS)} spot_relations")

    conn.commit()
    conn.close()

    # 5. 显示统计
    cur = sqlite3.connect(str(DB_PATH))
    print()
    print("📈 当前 db 状态:")
    tables = ["scenic_spots", "metric_snapshots", "content_assets",
              "decision_rules", "tourist_segments", "regions", "spot_relations"]
    for t in tables:
        cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {cnt}")
    cur.close()


if __name__ == "__main__":
    seed_all()
