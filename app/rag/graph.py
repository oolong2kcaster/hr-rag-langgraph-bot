from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.config import Settings
from app.domains.registry import DOMAIN_REGISTRY, Domain
from app.domains.router import route_domain
from app.domains.policy.agent import run_policy_agent
from app.domains.tax_2026.agent import run_tax_agent
from app.rag.citations import (
    ensure_citation_note,
    format_context,
    remap_answer_citations,
)
from app.rag.llm import OpenAIClients
from app.rag.prompts import build_rewrite_prompt
from app.rag.query_intent import DEFAULT_EXHAUSTIVE_KEYWORDS, is_exhaustive_question
from app.rag.retriever import HybridRetriever
from app.rag.state import RAGState

logger = logging.getLogger(__name__)


class HRRAGGraph:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = OpenAIClients(settings)
        self.retriever = HybridRetriever(settings)
        self.exhaustive_keywords = DEFAULT_EXHAUSTIVE_KEYWORDS
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(RAGState)
        builder.add_node("rewrite_query", self.rewrite_query)
        builder.add_node("route_domain", self.route_domain)
        builder.add_node("retrieve", self.retrieve)
        builder.add_node("rerank_and_grade", self.rerank_and_grade)
        builder.add_node("compress_context", self.compress_context)
        builder.add_node("domain_agent", self.domain_agent)
        builder.add_node("verify_answer", self.verify_answer)
        builder.add_node("retry_query", self.retry_query)

        builder.add_edge(START, "rewrite_query")
        builder.add_edge("rewrite_query", "route_domain")
        builder.add_edge("route_domain", "retrieve")
        builder.add_edge("retrieve", "rerank_and_grade")
        builder.add_conditional_edges(
            "rerank_and_grade",
            self.route_after_grade,
            {
                "retry_query": "retry_query",
                "compress_context": "compress_context",
            },
        )
        builder.add_edge("retry_query", "retrieve")
        builder.add_edge("compress_context", "domain_agent")
        builder.add_edge("domain_agent", "verify_answer")
        builder.add_edge("verify_answer", END)
        return builder.compile()

    def invoke(
        self,
        question: str,
        agent_id: str | None = None,
        domain_hint: str | None = None,
    ) -> RAGState:
        state: RAGState = {
            "question": question,
            "normalized_question": question.strip(),
            "agent_id": agent_id,
            "domain_hint": domain_hint,
            "retry_count": 0,
            "errors": [],
        }
        return self.graph.invoke(state)

    def rewrite_query(self, state: RAGState) -> RAGState:
        question = state["question"]
        try:
            rewritten = self.llm.chat(
                [
                    {
                        "role": "system",
                        "content": "Bạn rewrite query tìm kiếm, chỉ trả về query.",
                    },
                    {"role": "user", "content": build_rewrite_prompt(question)},
                ],
                temperature=0.0,
            ).strip()
            if not rewritten:
                rewritten = question
        except Exception as exc:  # noqa: BLE001
            logger.exception("Query rewrite failed; fallback to original question")
            state.setdefault("errors", []).append(f"rewrite_query failed: {exc}")
            rewritten = question
        return {"rewritten_query": rewritten}

    def route_domain(self, state: RAGState) -> RAGState:
        question = state.get("normalized_question") or state.get("question", "")
        is_exhaustive = is_exhaustive_question(question, self.exhaustive_keywords)

        hint = state.get("domain_hint")
        domain = self._safe_domain(hint) if hint else route_domain(question)
        if domain == Domain.UNKNOWN:
            domain = Domain.POLICY

        retrieval_filter: dict[str, str] = {}
        if domain in DOMAIN_REGISTRY:
            retrieval_filter = dict(DOMAIN_REGISTRY[domain].retrieval_filter)

        return {
            "domain": domain.value,
            "retrieval_filter": retrieval_filter,
            "is_exhaustive_query": is_exhaustive,
        }

    def retrieve(self, state: RAGState) -> RAGState:
        query = state.get("rewritten_query") or state["question"]
        docs = self.retriever.retrieve(
            query=query,
            agent_id=state.get("agent_id"),
            filters=state.get("retrieval_filter"),
            exhaustive=state.get("is_exhaustive_query"),
        )
        return {"retrieved_docs": docs}

    def rerank_and_grade(self, state: RAGState) -> RAGState:
        docs = state.get("retrieved_docs", [])
        ranked = docs
        top_score = max((float(d.get("score", 0.0)) for d in docs), default=0.0)
        needs_retry = (
            top_score < self.settings.min_relevance_score
            and state.get("retry_count", 0) < 1
        )
        confidence = min(1.0, max(0.0, top_score))
        return {
            "ranked_docs": ranked,
            "confidence": confidence,
            "needs_retry": needs_retry,
        }

    def route_after_grade(
        self, state: RAGState
    ) -> Literal["retry_query", "compress_context"]:
        return "retry_query" if state.get("needs_retry") else "compress_context"

    def retry_query(self, state: RAGState) -> RAGState:
        retry_count = int(state.get("retry_count", 0)) + 1
        question = state["question"]
        domain = state.get("domain")
        if domain == Domain.TAX_2026.value:
            suffix = "thuế tncn biểu thuế giảm trừ người phụ thuộc"
        else:
            suffix = "nội quy lao động chính sách nhân sự quy định điều khoản"
        return {
            "retry_count": retry_count,
            "rewritten_query": f"{question} {suffix}",
        }

    def compress_context(self, state: RAGState) -> RAGState:
        context, citations = format_context(
            state.get("ranked_docs", []), max_chars=self.settings.max_context_chars
        )
        return {"context": context, "citations": citations}

    def domain_agent(self, state: RAGState) -> RAGState:
        domain = state.get("domain")
        if domain == Domain.POLICY.value:
            return run_policy_agent(state, self.llm)
        if domain == Domain.TAX_2026.value:
            return run_tax_agent(state, self.llm)
        if not state.get("context", "").strip():
            return {
                "answer": "Tôi chưa xác định được nhóm nghiệp vụ phù hợp và chưa có đủ context để trả lời.",
            }
        return {"answer": "Tôi chưa xác định được nhóm nghiệp vụ phù hợp để trả lời câu hỏi này."}

    def verify_answer(self, state: RAGState) -> RAGState:
        citations = state.get("citations", [])
        answer = ensure_citation_note(state.get("answer", ""), citations)
        answer = remap_answer_citations(answer, citations)
        cited = [c["label"] for c in citations if f"[{c['label']}]" in answer]
        verification = {
            "has_context": bool(state.get("context")),
            "citation_count": len(citations),
            "cited_labels_in_answer": cited,
            "confidence": state.get("confidence", 0.0),
            "domain": state.get("domain"),
        }
        return {"answer": answer, "verification": verification}

    def _safe_domain(self, value: str | None, default: Domain = Domain.UNKNOWN) -> Domain:
        if not value:
            return default
        for domain in Domain:
            if domain.value == value:
                return domain
        return default
