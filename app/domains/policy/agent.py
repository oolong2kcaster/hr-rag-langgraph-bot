from __future__ import annotations

from app.domains.policy.prompts import POLICY_SYSTEM_PROMPT, build_policy_answer_prompt
from app.rag.llm import OpenAIClients
from app.rag.state import RAGState


def run_policy_agent(state: RAGState, llm: OpenAIClients) -> RAGState:
    context = state.get("context", "")
    if not context.strip():
        return {"answer": "Tôi chưa tìm thấy thông tin này trong tài liệu nội quy đã nạp."}

    answer = llm.chat(
        [
            {"role": "system", "content": POLICY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_policy_answer_prompt(state.get("question", ""), context),
            },
        ],
        temperature=0.0,
    ).strip()
    return {"answer": answer}
