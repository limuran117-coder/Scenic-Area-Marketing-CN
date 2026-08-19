#!/usr/bin/env python3
"""
Graphiti 本地化集成脚本 — 零 OpenAI 依赖
LLM: DeepSeek (openai 兼容, json_object 降级)
Embedding: Ollama bge-m3 (OpenAI 兼容端点)
Reranker: 无 (stub, 保留 BM25/图遍历顺序)
存储: FalkorDB (Docker, localhost:6379)
"""
import asyncio, json, os, sys
from datetime import datetime, timezone
from graphiti_core.graphiti import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.embedder.client import EmbedderClient
import httpx

class OllamaEmbedder(EmbedderClient):
    """直接用 httpx 调 Ollama 原生 /api/embed，绕开 OpenAI SDK 的 encoding_format=base64 触发 Ollama 502 的 bug"""
    def __init__(self, model: str = "bge-m3", base_url: str = "http://localhost:11434"):
        self.model = model
        self._api = base_url + "/api/embed"
        # trust_env=False: 禁用系统代理(127.0.0.1:7897 抓站代理会劫持本地请求返回 502)
        self._client = httpx.AsyncClient(timeout=120, trust_env=False)

    @property
    def config(self):
        return None

    async def create(self, input_data) -> list[float]:
        # Graphiti fallback 传 ['str']，也可能传裸字符串
        if isinstance(input_data, list):
            input_data = input_data[0] if input_data else ""
        # Ollama 0.32.9 bug: /api/embed 对 application/json 返回 502，必须用 form-urlencoded
        r = await self._client.post(self._api, data=json.dumps({"model": self.model, "input": input_data}), headers={"Content-Type": "application/x-www-form-urlencoded"})
        r.raise_for_status()
        return r.json()["embeddings"][0]

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        # trust_env=False 已绕开代理；若批量仍失败则逐条
        try:
            r = await self._client.post(self._api, json={"model": self.model, "input": input_data_list})
            r.raise_for_status()
            return r.json()["embeddings"]
        except Exception:
            out = []
            for item in input_data_list:
                vec = await self.create(item)
                out.append(vec)
            return out

    async def close(self):
        await self._client.aclose()

from graphiti_core.cross_encoder.client import CrossEncoderClient

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
OLLAMA_URL = "http://localhost:11434"

class NoopReranker(CrossEncoderClient):
    """跳过 rerank 的 stub — 保持图结构搜索顺序"""
    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        return [(p, 1.0) for p in passages]

class OllamaReranker(CrossEncoderClient):
    """基于 bge-m3 embedding 的余弦重排器（零新模型、零内存压力）
    
    用 Ollama /api/embed 对 (query, passage) 各自编码，算余弦相似度排序。
    效果介于 Noop 和真 cross-encoder 之间，但完全本地、无新依赖。
    """
    def __init__(self, embedder: OllamaEmbedder):
        self._embedder = embedder

    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        if not passages:
            return []
        try:
            q_vec = await self._embedder.create(query)
            p_vecs = await self._embedder.create_batch(passages)
            scores = []
            for p, pv in zip(passages, p_vecs):
                sim = sum(a * b for a, b in zip(q_vec, pv))
                qn = sum(a * a for a in q_vec) ** 0.5
                pn = sum(b * b for b in pv) ** 0.5
                if qn == 0 or pn == 0:
                    scores.append((p, 0.0))
                else:
                    scores.append((p, sim / (qn * pn)))
            return sorted(scores, key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"⚠️ reranker 降级为原始顺序: {e}")
            return [(p, 1.0) for p in passages]

def build_client() -> Graphiti:
    llm_config = LLMConfig(
        api_key=DEEPSEEK_KEY,
        model="deepseek-v4-flash",
        base_url="https://api.deepseek.com/v1",
    )
    llm = OpenAIGenericClient(
        config=llm_config,
        structured_output_mode='json_object',  # DeepSeek 不支持 json_schema
    )
    embedder = OllamaEmbedder(model="bge-m3", base_url=OLLAMA_URL)
    driver = FalkorDriver(host="localhost", port=6379, database="graphiti")
    return Graphiti(
        graph_driver=driver,
        llm_client=llm,
        embedder=embedder,
        cross_encoder=OllamaReranker(embedder),
    )

async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    g = build_client()
    if mode == "init":
        await g.build_indices_and_constraints()
        print("✅ 索引/约束构建完成")
        return

    if mode == "add":
        content = sys.argv[2]
        await g.add_episode(
            name="episode",
            episode_body=content,
            source_description="manual local entry",
            reference_time=datetime.now(timezone.utc),
            group_id="movie-town",
        )
        print(f"✅ 已写入 episode: {content[:60]}...")
        return

    if mode == "search":
        query = sys.argv[2]
        results = await g.search(query, group_ids=["movie-town"])
        print(f"🔍 查询: {query}")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. {r.fact} [valid: {r.valid_at}]")
        return

    if mode == "test":
        # 冒烟测试: 写入一条 → 检索
        await g.build_indices_and_constraints()
        await g.add_episode(
            name="smoke",
            episode_body="郑州电影小镇2026年目标客流123万，营收1.2亿，8月15日单日客流10237创暑期新高",
            source_description="smoke test",
            reference_time=datetime.now(timezone.utc),
            group_id="movie-town",
        )
        results = await g.search("电影小镇客流目标", group_ids=["movie-town"])
        print("冒烟测试:", [(r.fact, str(r.valid_at)) for r in results[:3]])
        return

    print("用法: graphiti_local.py [init|add <内容>|search <query>|test]")

if __name__ == "__main__":
    asyncio.run(main())
