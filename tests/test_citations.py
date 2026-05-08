from app.rag.citations import remap_answer_citations


def test_remap_answer_citations_maps_fact_to_matching_chunk():
    answer = "Thời hiệu chung là 06 tháng [Page 1]."
    citations = [
        {
            "label": "Page 1",
            "context_text": "Quyết định xử lý bồi thường thiệt hại áp dụng theo quy trình.",
        },
        {
            "label": "Page 2",
            "context_text": "a. Thời hiệu xử lý bồi thường thiệt hại là 06 tháng kể từ ngày xảy ra vụ việc.",
        },
    ]

    remapped = remap_answer_citations(answer, citations)
    assert "[Page 2]" in remapped
    assert "[Page 1]" not in remapped
