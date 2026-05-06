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


def test_split_text_legal_sections_preserve_clause_boundaries():
    text = (
        "a. Thời hiệu xử lý bồi thường thiệt hại là 06 tháng kể từ ngày xảy ra vụ việc.\n"
        "Không xử lý trong thời gian Điều 25.10.\n\n"
        "b. Trường hợp đặc biệt có thể kéo dài thêm nhưng không quá 60 ngày."
    )
    chunks = split_text(text, chunk_size=500, chunk_overlap=50)

    assert len(chunks) == 2
    assert chunks[0].startswith("a.")
    assert "06 tháng" in chunks[0]
    assert chunks[1].startswith("b.")
    assert "60 ngày" in chunks[1]
