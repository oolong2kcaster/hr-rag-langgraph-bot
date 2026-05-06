from __future__ import annotations

import logging
import math
import re
from collections import defaultdict
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

from app.config import Settings
from app.rag.llm import OpenAIClients
from app.storage.qdrant_store import QdrantVectorStore

logger = logging.getLogger(__name__)


def tokenize(text: str) -> list[str]:
    # Unicode-friendly enough for Vietnamese phase 1. For better VN search later, add underthesea/VnCoreNLP.
    return re.findall(r"[\wÀ-ỹ]+", (text or "").lower(), flags=re.UNICODE)


def normalize_scores(items: list[dict[str, Any]], key: str) -> dict[str, float]:
    values = [float(i.get(key, 0.0)) for i in items]
    if not values:
        return {}
    min_v, max_v = min(values), max(values)
    if math.isclose(min_v, max_v):
        return {str(i["id"]): 1.0 if max_v > 0 else 0.0 for i in items}
    return {str(i["id"]): (float(i.get(key, 0.0)) - min_v) / (max_v - min_v) for i in items}


class HybridRetriever:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = OpenAIClients(settings)
        self.store = QdrantVectorStore(settings)

    def retrieve(self, query: str, agent_id: str | None = None) -> list[dict[str, Any]]:
        query_vector = self.llm.embed([query])[0]

        semantic = self.store.search(
            query_vector,
            limit=self.settings.semantic_candidates,
            agent_id=agent_id,
        )

        # Phase 1 hybrid lexical retrieval: BM25 over current Qdrant payloads.
        corpus = self.store.scroll_payloads(limit=5000, agent_id=agent_id)
        lexical = self._bm25(query, corpus, limit=self.settings.semantic_candidates)

        merged = self._merge(semantic, lexical)
        ranked = sorted(merged, key=lambda d: d.get("score", 0.0), reverse=True)
        return ranked[: self.settings.retrieval_top_k]

    def _bm25(self, query: str, corpus: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        if not corpus:
            return []
        tokenized = [tokenize(doc.get("text", "")) for doc in corpus]
        bm25 = BM25Okapi(tokenized)
        scores = bm25.get_scores(tokenize(query))
        top_indices = np.argsort(scores)[::-1][:limit]
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0:
                continue
            item = dict(corpus[int(idx)])
            item["lexical_score"] = score
            results.append(item)
        return results

    def _merge(self, semantic: list[dict], lexical: list[dict]) -> list[dict]:
        by_id: dict[str, dict] = {}
        for item in semantic + lexical:
            by_id.setdefault(str(item["id"]), {}).update(item)

        semantic_norm = normalize_scores(semantic, "semantic_score")
        lexical_norm = normalize_scores(lexical, "lexical_score")

        for item_id, item in by_id.items():
            sem = semantic_norm.get(item_id, 0.0)
            lex = lexical_norm.get(item_id, 0.0)
            item["score"] = round(0.68 * sem + 0.32 * lex, 6)
            item["score_breakdown"] = {"semantic": round(sem, 4), "lexical": round(lex, 4)}
        return list(by_id.values())
