#!/bin/bash
# ingest_pipeline.sh — 抖音指数 Ontology 双轨写入管道
# Phase 4 核心脚本：D-051 确认必须 cd scripts/ 才能让 adapter 正确导入 ontology.ontology_store
#
# 执行流程：
#   1. cd 到 scripts/ 目录（解决 import 路径依赖）
#   2. 运行 douyin_index.py → /tmp/crawl_data.json
#   3. 运行 adapter-douyin.py 读取 /tmp/crawl_data.json
#   4. 双轨写入：JSON 文件 + SQLite（via write_to_sqlite）
#
# 用法：
#   bash ingest_pipeline.sh          # 完整执行
#   bash ingest_pipeline.sh --dry    # 仅验证，不采集
#
# cron 集成示例：
#   30 10 * * 1-5 cd /Users/tianjinzhan/.openclaw/workspace/scripts && bash ingest_pipeline.sh >> /tmp/ingest_pipeline.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK_PATH="/tmp/douyin_crawl.lock"
CRAWL_DATA="/tmp/crawl_data.json"
DRY_RUN=false

# 解析参数
if [[ "${1:-}" == "--dry" ]]; then
    DRY_RUN=true
    echo "[DRY] 模式：仅验证，不采集数据"
fi

echo "========== $(date '+%Y-%m-%d %H:%M:%S') =========="
echo "[INGEST] 工作目录: $SCRIPT_DIR"

# --- 前置锁检查 ---
if [[ -f "$LOCK_PATH" ]]; then
    LOCK_AGE=$(($(date +%s) - $(stat -f %Sm -t %s "$LOCK_PATH" 2>/dev/null || stat -c %Y "$LOCK_PATH" 2>/dev/null)))
    if [[ "$LOCK_AGE" -lt 3600 ]]; then
        echo "[SKIP] 锁文件存在（${LOCK_AGE}s 前创建），可能有其他实例在跑，退出"
        exit 0
    else
        echo "[WARN] 锁文件过期（${LOCK_AGE}s），删除后继续"
        rm -f "$LOCK_PATH"
    fi
fi

# --- Step 1: 数据采集（douyin_index.py）---
if [[ "$DRY_RUN" == "false" ]]; then
    echo "[STEP1] 启动抖音指数采集..."
    touch "$LOCK_PATH"

    # douyin_index.py 输出到 /tmp/crawl_data.json
    # 代理和 cookie 已在脚本内硬编码（--proxy 127.0.0.1:7897）
    cd "$SCRIPT_DIR"
    python3 douyin_index.py
    CRAWL_EXIT=$?

    rm -f "$LOCK_PATH"

    if [[ "$CRAWL_EXIT" -ne 0 ]]; then
        echo "[ERROR] douyin_index.py 采集失败，exit=$CRAWL_EXIT"
        exit 1
    fi

    if [[ ! -f "$CRAWL_DATA" ]]; then
        echo "[ERROR] douyin_index.py 未生成 $CRAWL_DATA"
        exit 1
    fi

    CRAWL_LINES=$(wc -l < "$CRAWL_DATA")
    echo "[STEP1] 采集完成: $(wc -c < "$CRAWL_DATA") bytes, $CRAWL_LINES lines"
else
    echo "[STEP1] 跳过（dry mode）"
fi

# --- Step 2: Ontology 双轨写入（adapter-douyin.py）---
echo "[STEP2] 运行 adapter-douyin.py（cd 到 scripts/ 后执行）..."

cd "$SCRIPT_DIR"
python3 adapter-douyin.py --input "$CRAWL_DATA"
ADAPTER_EXIT=$?

if [[ "$ADAPTER_EXIT" -ne 0 ]]; then
    echo "[ERROR] adapter-douyin.py 失败，exit=$ADAPTER_EXIT"
    exit 1
fi

echo "[DONE] 双轨写入完成 $(date '+%Y-%m-%d %H:%M:%S')"
