from __future__ import annotations

from app.domains.registry import Domain

POLICY_KEYWORDS = (
    "nội quy",
    "nghỉ phép",
    "nghỉ hằng năm",
    "nghỉ năm",
    "đi muộn",
    "kỷ luật",
    "bồi thường",
    "lao động",
    "công ty",
)

TAX_KEYWORDS = (
    "thuế",
    "tncn",
    "thu nhập cá nhân",
    "giảm trừ",
    "người phụ thuộc",
    "biểu thuế",
    "gross",
    "net",
)


def route_domain(question: str) -> Domain:
    q = (question or "").lower()
    if any(keyword in q for keyword in TAX_KEYWORDS):
        return Domain.TAX_2026
    if any(keyword in q for keyword in POLICY_KEYWORDS):
        return Domain.POLICY
    return Domain.UNKNOWN
