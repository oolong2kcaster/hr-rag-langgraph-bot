from app.rag.query_intent import (
    DEFAULT_EXHAUSTIVE_KEYWORDS,
    is_exhaustive_question,
    parse_keywords,
)


def test_parse_keywords_fallback_default():
    assert parse_keywords("") == DEFAULT_EXHAUSTIVE_KEYWORDS


def test_parse_keywords_csv():
    assert parse_keywords("all, list,  ") == ("all", "list")


def test_is_exhaustive_question():
    assert is_exhaustive_question(
        "Hãy liệt kê tất cả trường hợp nghỉ phép", DEFAULT_EXHAUSTIVE_KEYWORDS
    )
    assert not is_exhaustive_question("Nghỉ phép năm bao nhiêu ngày", ("foo", "bar"))
