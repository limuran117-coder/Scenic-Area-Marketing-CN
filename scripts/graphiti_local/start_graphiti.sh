#!/bin/bash
# Graphiti 本地知识图谱一键启动脚本
# 用法: ./start_graphiti.sh
# 依赖: Docker (FalkorDB), Ollama (bge-m3), Python venv

set -e
echo "=== 🚀 Graphiti 本地服务启动 ==="

# 1. FalkorDB (Docker) —— 挂载点必须是 /var/lib/falkordb/data（Redis 实际读写路径）
#    不是 /data（那是软链目录，挂那里数据不持久化，8/19 踩坑）
if ! docker ps --format '{{.Names}}' | grep -q '^graphiti-falkordb$'; then
    echo "[1/3] 启动 FalkorDB..."
    docker start graphiti-falkordb 2>/dev/null || docker run -d --name graphiti-falkordb -p 6379:6379 -p 3000:3000 -v graphiti-data:/var/lib/falkordb/data falkordb/falkordb:latest
    sleep 2
else
    echo "[1/3] FalkorDB 已在运行 ✅"
fi

# 2. Ollama embedding 模型
if ! curl -s -m 3 http://localhost:11434/api/tags | grep -q "bge-m3"; then
    echo "[2/3] 拉取 bge-m3 embedding 模型..."
    ollama pull bge-m3
else
    echo "[2/3] bge-m3 已就绪 ✅"
fi

# 3. Python venv
VENV=/tmp/graphiti-venv
if [ ! -f "$VENV/bin/python" ]; then
    echo "[3/3] 创建 Python venv..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet graphiti-core falkordb redis httpx
else
    echo "[3/3] venv 已就绪 ✅"
fi

echo ""
echo "=== ✅ Graphiti 本地服务就绪 ==="
echo "FalkorDB:   localhost:6379 (Dashboard: localhost:3000)"
echo "Embedding:  Ollama bge-m3 (localhost:11434)"
echo "LLM:        DeepSeek (需 DEEPSEEK_API_KEY 环境变量)"
echo ""
echo "使用示例:"
echo "  DEEPSEEK_API_KEY=xxx $VENV/bin/python ~/.openclaw/workspace/scripts/graphiti_local/graphiti_local.py add '郑州电影小镇8月16日客流9036人'"
echo "  DEEPSEEK_API_KEY=xxx $VENV/bin/python ~/.openclaw/workspace/scripts/graphiti_local/graphiti_local.py search '电影小镇客流'"
