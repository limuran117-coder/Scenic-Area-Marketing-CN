-- ============================================
-- 001_initial.sql
-- 电影小镇 Ontology Store 初始 Schema
-- 日期: 2026-06-19
-- 设计参考: 本地接入方案.md §2.3
-- ============================================

-- 元数据表（记录 schema 版本）
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO schema_meta (key, value) VALUES
    ('schema_version', '1.0.0'),
    ('ontology_version', '1.1.4'),
    ('created_at', datetime('now'));

-- ==========================================
-- 1. 对象表（核心数据）
-- ==========================================

-- 景区实体
CREATE TABLE IF NOT EXISTS scenic_spots (
    id          TEXT PRIMARY KEY,        -- ss_<name> 或 ontology.json 中的 id
    name        TEXT NOT NULL,
    short_name  TEXT,
    category    TEXT,                    -- theme_park/historical/nature/cultural_town
    tier        TEXT,                    -- primary/secondary/national
    province    TEXT,
    city        TEXT,
    location    TEXT,
    is_core_competitor INTEGER DEFAULT 0,
    annual_capacity REAL,                -- 万人
    tags        TEXT,                    -- JSON array
    competitors TEXT,                    -- JSON array of spot_ids
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

-- 指标快照（核心写入表——每天插入新行）
CREATE TABLE IF NOT EXISTS metric_snapshots (
    id             TEXT PRIMARY KEY,    -- ms_<source>_<date>_<spot>_<metric>
    spot_id        TEXT NOT NULL REFERENCES scenic_spots(id),
    source         TEXT NOT NULL,        -- douyin / xiaohongshu / visitors / baidu
    date           TEXT NOT NULL,        -- YYYY-MM-DD
    metric_type    TEXT NOT NULL,        -- search_index/comprehensive_index/visitor_count/...
    value          REAL NOT NULL,
    daily_change   REAL,                 -- 日环比（%）
    weekly_change  REAL,
    confidence     REAL DEFAULT 0.5,     -- 0.0-1.0
    raw_data       TEXT,                 -- JSON: 原始数据备份
    metadata       TEXT,                 -- JSON: 业务元数据
    ingested_at    TEXT DEFAULT (datetime('now')),
    UNIQUE(spot_id, source, date, metric_type)
);
CREATE INDEX IF NOT EXISTS idx_ms_spot_date ON metric_snapshots(spot_id, date);
CREATE INDEX IF NOT EXISTS idx_ms_source_date ON metric_snapshots(source, date);
CREATE INDEX IF NOT EXISTS idx_ms_metric_type ON metric_snapshots(metric_type);

-- 内容资产（小红书笔记、抖音视频等）
CREATE TABLE IF NOT EXISTS content_assets (
    id             TEXT PRIMARY KEY,    -- ca_<source>_<id>
    schema         TEXT DEFAULT 'ContentAsset',
    source         TEXT NOT NULL,        -- xiaohongshu / douyin / weibo
    external_id    TEXT,                 -- 平台原始ID
    spot_id        TEXT REFERENCES scenic_spots(id),
    title          TEXT,
    description    TEXT,
    url            TEXT,
    author         TEXT,
    author_id      TEXT,
    like_count     INTEGER DEFAULT 0,
    comment_count  INTEGER DEFAULT 0,
    share_count    INTEGER DEFAULT 0,
    publish_date   TEXT,
    content_type   TEXT,                 -- video / note / article / live
    platform       TEXT,                 -- adapter 字段映射 source -> platform
    notes_count    INTEGER DEFAULT 0,
    metrics        TEXT,                 -- JSON: 嵌套指标
    sentiment      TEXT,                 -- positive/neutral/negative/mixed
    tags           TEXT,                 -- JSON array
    is_viral       INTEGER DEFAULT 0,
    raw_data       TEXT,                 -- 原始数据备份
    derived_to_metric_snapshot TEXT,     -- 反向引用
    ingested_at    TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ca_spot ON content_assets(spot_id);
CREATE INDEX IF NOT EXISTS idx_ca_source ON content_assets(source);
CREATE INDEX IF NOT EXISTS idx_ca_date ON content_assets(publish_date);

-- 事件/动态（竞品活动、行业趋势、政策）
CREATE TABLE IF NOT EXISTS events (
    id             TEXT PRIMARY KEY,    -- ev_<type>_<date>_<seq>
    schema         TEXT DEFAULT 'Event',
    title          TEXT NOT NULL,
    type           TEXT NOT NULL,        -- competitor_activity/industry_trend/policy_change/sentiment_incident
    severity       TEXT DEFAULT 'info',  -- info/watch/warning/critical
    description    TEXT,
    source         TEXT,                 -- 信息来源
    url            TEXT,
    occurred_at    TEXT NOT NULL,
    detected_at    TEXT,
    expires_at     TEXT,
    related_spots  TEXT,                 -- JSON array of spot_ids
    tags           TEXT,                 -- JSON array
    raw_data       TEXT,
    ingested_at    TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);

-- 营销活动
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id             TEXT PRIMARY KEY,    -- mc_<name>
    schema         TEXT DEFAULT 'MarketingCampaign',
    name           TEXT NOT NULL,
    spot_id        TEXT REFERENCES scenic_spots(id),
    type           TEXT,                 -- seasonal_event/price_promotion/kol_collab/...
    start_date     TEXT,
    end_date       TEXT,
    budget         REAL,
    channels       TEXT,                 -- JSON array
    target_audience TEXT,                -- JSON array
    kpis           TEXT,                 -- JSON: {"visitors": 1000, "revenue": 50000}
    expected_impact TEXT,
    actual_impact  TEXT,
    status         TEXT DEFAULT 'planned',
    notes          TEXT,
    created_at     TEXT DEFAULT (datetime('now'))
);

-- 决策规则
CREATE TABLE IF NOT EXISTS decision_rules (
    id             TEXT PRIMARY KEY,    -- dr_<rule_id>
    schema         TEXT DEFAULT 'DecisionRule',
    rule_id        TEXT NOT NULL,        -- 如 R-001
    name           TEXT NOT NULL,
    category       TEXT,                 -- content_strategy/pricing/alert/...
    condition      TEXT NOT NULL,
    action         TEXT NOT NULL,
    authority_tier INTEGER,              -- 1-9
    conflict_rule  TEXT,
    confidence     REAL DEFAULT 0.5,
    status         TEXT DEFAULT 'hypothesis',  -- hypothesis/verified/invalidated/obsolete
    source         TEXT,
    trigger_count  INTEGER DEFAULT 0,
    last_triggered_at TEXT,
    raw_data       TEXT,
    updated_at     TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_dr_status ON decision_rules(status);

-- 客群细分
CREATE TABLE IF NOT EXISTS tourist_segments (
    id             TEXT PRIMARY KEY,    -- ts_<name>
    schema         TEXT DEFAULT 'TouristSegment',
    name           TEXT NOT NULL,
    description    TEXT,
    age_range      TEXT,                 -- "18-25"
    gender_split   TEXT,                 -- JSON: {"male": 0.4, "female": 0.6}
    region         TEXT,                 -- 主要客源地
    characteristics TEXT,                -- JSON: 行为特征
    tags           TEXT,
    created_at     TEXT DEFAULT (datetime('now'))
);

-- 区域（地理）
CREATE TABLE IF NOT EXISTS regions (
    id             TEXT PRIMARY KEY,    -- rg_<name>
    schema         TEXT DEFAULT 'Region',
    name           TEXT NOT NULL,
    level          TEXT,                 -- province/city/district
    parent_id      TEXT REFERENCES regions(id),
    aliases        TEXT,                 -- JSON array
    raw_data       TEXT,
    created_at     TEXT DEFAULT (datetime('now'))
);

-- ==========================================
-- 2. 关系表（Link Types 实例化）
-- ==========================================

-- 景区间关系
CREATE TABLE IF NOT EXISTS spot_relations (
    source_id      TEXT NOT NULL REFERENCES scenic_spots(id),
    target_id      TEXT NOT NULL REFERENCES scenic_spots(id),
    relation_type  TEXT NOT NULL,        -- competes_with/located_in/...
    confidence     REAL DEFAULT 0.8,
    updated_at     TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (source_id, target_id, relation_type)
);

-- 事件-景区关联
CREATE TABLE IF NOT EXISTS event_spot_links (
    event_id       TEXT NOT NULL REFERENCES events(id),
    spot_id        TEXT NOT NULL REFERENCES scenic_spots(id),
    relevance      REAL DEFAULT 1.0,
    PRIMARY KEY (event_id, spot_id)
);

-- 指标-内容资产双向引用
CREATE TABLE IF NOT EXISTS metric_content_links (
    metric_id      TEXT NOT NULL REFERENCES metric_snapshots(id),
    content_id     TEXT NOT NULL REFERENCES content_assets(id),
    link_type      TEXT DEFAULT 'aggregated_from',  -- aggregated_from / contributes_to
    PRIMARY KEY (metric_id, content_id, link_type)
);

-- 营销活动-景区
CREATE TABLE IF NOT EXISTS campaign_spot_links (
    campaign_id    TEXT NOT NULL REFERENCES marketing_campaigns(id),
    spot_id        TEXT NOT NULL REFERENCES scenic_spots(id),
    PRIMARY KEY (campaign_id, spot_id)
);

-- ==========================================
-- 3. 审计与元数据
-- ==========================================

-- 接入日志
CREATE TABLE IF NOT EXISTS ingest_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    adapter_name   TEXT NOT NULL,
    status         TEXT NOT NULL,        -- success/partial/failed
    source_file    TEXT,
    records_added  INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message  TEXT,
    started_at     TEXT,
    finished_at    TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ilg_adapter ON ingest_log(adapter_name);

-- 查询日志
CREATE TABLE IF NOT EXISTS query_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    query_name     TEXT NOT NULL,
    query_type     TEXT,                 -- cross_type/trend/comparison/...
    result_count   INTEGER,
    latency_ms     INTEGER,
    queried_at     TEXT DEFAULT (datetime('now'))
);

-- Action 日志
CREATE TABLE IF NOT EXISTS action_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type    TEXT NOT NULL,        -- send_card/create_alert/update_dashboard
    target         TEXT,
    payload_summary TEXT,
    status         TEXT,                 -- queued/sent/failed
    error_message  TEXT,
    created_at     TEXT DEFAULT (datetime('now'))
);

-- ==========================================
-- 4. 视图（常用查询预定义）
-- ==========================================

-- 抖音8景区今日排名视图
DROP VIEW IF EXISTS v_douyin_ranking;
CREATE VIEW v_douyin_ranking AS
SELECT
    s.id AS 景区ID,
    s.name AS 景区,
    ms_search.value AS 搜索指数,
    ms_search.daily_change AS 搜索日环比,
    ms_comp.value AS 综合指数,
    ms_comp.daily_change AS 综合日环比,
    ms_search.date AS 数据日期
FROM scenic_spots s
LEFT JOIN metric_snapshots ms_search
    ON ms_search.spot_id = s.id
    AND ms_search.source = 'douyin'
    AND ms_search.metric_type = 'search_index'
LEFT JOIN metric_snapshots ms_comp
    ON ms_comp.spot_id = s.id
    AND ms_comp.source = 'douyin'
    AND ms_comp.metric_type = 'composite_index'
    AND ms_comp.date = ms_search.date
WHERE ms_search.date = (SELECT MAX(date) FROM metric_snapshots
                          WHERE source = 'douyin' AND metric_type = 'search_index')
ORDER BY ms_search.value DESC;

-- 跨源趋势视图
DROP VIEW IF EXISTS v_weekly_trend;
CREATE VIEW v_weekly_trend AS
SELECT
    s.name AS 景区,
    ms.metric_type AS 指标,
    ms.source AS 数据源,
    ms.date AS 日期,
    ms.value AS 数值,
    ms.daily_change AS 日环比
FROM metric_snapshots ms
JOIN scenic_spots s ON ms.spot_id = s.id
WHERE ms.date >= date('now', '-7 days')
ORDER BY s.name, ms.metric_type, ms.date;

-- 7天内容增量视图
DROP VIEW IF EXISTS v_content_growth;
CREATE VIEW v_content_growth AS
SELECT
    s.name AS 景区,
    ca.source AS 平台,
    ca.notes_count AS 内容数,
    ca.publish_date AS 发布日期
FROM content_assets ca
JOIN scenic_spots s ON ca.spot_id = s.id
WHERE ca.publish_date >= date('now', '-7 days')
ORDER BY ca.publish_date DESC, s.name;

-- ==========================================
-- 5. 种子数据（ScenicSpot 主表）
-- ==========================================
INSERT OR IGNORE INTO scenic_spots (id, name, short_name, category, tier, is_core_competitor) VALUES
    ('movie_town', '建业电影小镇', '电影小镇', 'cultural_town', 'primary', 1),
    ('only_henan', '只有河南·戏剧幻城', '只有河南', 'cultural_town', 'primary', 1),
    ('yinji_animal_kingdom', '银基动物王国', '银基动物王国', 'theme_park', 'primary', 1),
    ('wansuishan', '万岁山武侠城', '万岁山', 'historical', 'primary', 1),
    ('fangte_joy', '方特欢乐世界', '方特', 'theme_park', 'primary', 1),
    ('qingming_riverside', '清明上河园', '清明上河园', 'historical', 'primary', 1);

-- 补充 seed: 适配器输出中出现的额外景区 ID（保留与 adapter ID 一致）
INSERT OR IGNORE INTO scenic_spots (id, name, short_name, category, tier, is_core_competitor) VALUES
    ('fangte', '方特欢乐世界', '方特', 'theme_park', 'primary', 1),
    ('yinji', '银基动物王国', '银基', 'theme_park', 'primary', 1),
    ('wansui_mountain', '万岁山武侠城', '万岁山', 'historical', 'primary', 1),
    ('only_dream', '只有河南·戏剧幻城', '只有河南', 'cultural_town', 'primary', 1),
    ('haichang', '海昌海洋公园', '海昌', 'theme_park', 'secondary', 0),
    ('大唐不夜城', '大唐不夜城', '大唐不夜城', 'cultural_town', 'secondary', 0),
    ('海昌海洋公园', '海昌海洋公园', '海昌', 'theme_park', 'secondary', 0);
