from app.ingestion.chunker import split_text


def test_split_text_keeps_content():
    text = "Đoạn một nói về nghỉ phép.\n\nĐoạn hai nói về lương thưởng."
    chunks = split_text(text, chunk_size=50, chunk_overlap=10)
    joined = " ".join(chunks)
    assert "nghỉ phép" in joined
    assert "lương thưởng" in joined


def test_split_text_validates_overlap():
    try:
        split_text("abc", chunk_size=10, chunk_overlap=10)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
