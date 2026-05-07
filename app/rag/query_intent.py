from __future__ import annotations

DEFAULT_EXHAUSTIVE_KEYWORDS = (
    "tất cả",
    "toàn bộ",
    "liệt kê",
    "các trường hợp",
    "những trường hợp",
    "bao gồm",
    "đầy đủ",
)


def parse_keywords(csv_keywords: str | None) -> tuple[str, ...]:
    if not csv_keywords:
        return DEFAULT_EXHAUSTIVE_KEYWORDS
    values = [v.strip().lower() for v in csv_keywords.split(",")]
    keywords = tuple(v for v in values if v)
    return keywords or DEFAULT_EXHAUSTIVE_KEYWORDS


def is_exhaustive_question(question: str, keywords: tuple[str, ...]) -> bool:
    q = (question or "").lower()
    return any(keyword in q for keyword in keywords)
