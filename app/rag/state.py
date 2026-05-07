from __future__ import annotations

from typing import Any, TypedDict


class RAGState(TypedDict, total=False):
    question: str
    normalized_question: str
    domain: str
    domain_hint: str | None
    retrieval_filter: dict[str, Any]
    is_exhaustive_query: bool
    agent_id: str | None
    rewritten_query: str
    retrieved_docs: list[dict[str, Any]]
    ranked_docs: list[dict[str, Any]]
    context: str
    tool_result: dict[str, Any] | None
    answer: str
    citations: list[dict[str, Any]]
    confidence: float
    retry_count: int
    needs_retry: bool
    verification: dict[str, Any]
    errors: list[str]
