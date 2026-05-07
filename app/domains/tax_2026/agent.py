from __future__ import annotations

import re

from app.domains.tax_2026.prompts import TAX_SYSTEM_PROMPT, build_tax_answer_prompt
from app.domains.tax_2026.tools import calculate_personal_income_tax_2026
from app.rag.llm import OpenAIClients
from app.rag.state import RAGState


def _parse_monthly_income_vnd(question: str) -> float | None:
    q = (question or "").lower()

    million_match = re.search(r"(\d+(?:[.,]\d+)?)\s*triệu", q)
    if million_match:
        raw = million_match.group(1).replace(",", ".")
        return float(raw) * 1_000_000

    vnd_match = re.search(r"(\d[\d.,]*)\s*(?:vnd|đ|dong)?", q)
    if not vnd_match:
        return None
    raw = vnd_match.group(1).replace(".", "").replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def run_tax_agent(state: RAGState, llm: OpenAIClients) -> RAGState:
    context = state.get("context", "")
    if not context.strip():
        return {
            "answer": "Tôi chưa có đủ tài liệu/căn cứ thuế TNCN 2026 trong hệ thống để xác nhận chính xác."
        }

    tool_result = None
    income = _parse_monthly_income_vnd(state.get("question", ""))
    if income is not None:
        tool_result = calculate_personal_income_tax_2026(income)

    answer = llm.chat(
        [
            {"role": "system", "content": TAX_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_tax_answer_prompt(
                    state.get("question", ""),
                    context,
                    tool_result,
                ),
            },
        ],
        temperature=0.0,
    ).strip()

    return {
        "answer": answer,
        "tool_result": tool_result,
    }
