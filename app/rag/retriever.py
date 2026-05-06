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
        top_k = max(1, int(self.settings.retrieval_top_k))
        top_docs = ranked[:top_k]
        expanded = self._expand_with_neighbors(top_docs=top_docs, corpus=corpus)
        ordered = self._sort_for_context(expanded)
        self._check_limits(ordered, top_k=top_k)
        return ordered

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

    def _expand_with_neighbors(
        self,
        top_docs: list[dict[str, Any]],
        corpus: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        window = max(0, int(self.settings.retrieval_neighbor_window))
        if not top_docs or window <= 0:
            return top_docs

        by_id: dict[str, dict[str, Any]] = {str(doc["id"]): dict(doc) for doc in top_docs}

        by_doc_and_chunk: dict[tuple[str, str, int], dict[str, Any]] = {}
        for doc in corpus:
            chunk_index = doc.get("chunk_index")
            if chunk_index is None:
                continue
            key = (str(doc.get("agent_id") or ""), str(doc.get("source_path") or ""), int(chunk_index))
            by_doc_and_chunk[key] = doc

        for doc in top_docs:
            base_chunk = doc.get("chunk_index")
            if base_chunk is None:
                continue
            base_agent = str(doc.get("agent_id") or "")
            base_source = str(doc.get("source_path") or "")
            for offset in range(-window, window + 1):
                neighbor_key = (base_agent, base_source, int(base_chunk) + offset)
                neighbor = by_doc_and_chunk.get(neighbor_key)
                if not neighbor:
                    continue
                neighbor_id = str(neighbor.get("id"))
                if neighbor_id in by_id:
                    continue
                merged_neighbor = dict(neighbor)
                merged_neighbor["score"] = 0.0
                merged_neighbor["score_breakdown"] = {"semantic": 0.0, "lexical": 0.0}
                by_id[neighbor_id] = merged_neighbor
        return list(by_id.values())

    def _sort_for_context(self, docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        def to_int_or_default(value: Any, default: int) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def key(doc: dict[str, Any]) -> tuple:
            source = str(doc.get("source_name") or doc.get("source_path") or "")
            page = to_int_or_default(doc.get("page"), 10**9)
            chunk = to_int_or_default(doc.get("chunk_index"), 10**9)
            score = float(doc.get("score", 0.0))
            doc_id = str(doc.get("id", ""))
            return (source, page, chunk, -score, doc_id)

        return sorted(docs, key=key)

    def _check_limits(self, docs: list[dict[str, Any]], top_k: int) -> None:
        window = max(0, int(self.settings.retrieval_neighbor_window))
        max_docs = top_k * (2 * window + 1)
        if len(docs) > max_docs:
            logger.warning(
                "Retriever returned %s docs > max expected=%s (top_k=%s, window=%s).",
                len(docs),
                max_docs,
                top_k,
                window,
            )
