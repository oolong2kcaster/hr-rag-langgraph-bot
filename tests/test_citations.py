from app.rag.citations import remap_answer_citations


def test_remap_answer_citations_maps_fact_to_matching_chunk():
    answer = "Thời hiệu chung là 06 tháng [S1]."
    citations = [
        {
            "label": "S1",
            "context_text": "Quyết định xử lý bồi thường thiệt hại áp dụng theo quy trình.",
        },
        {
            "label": "S2",
            "context_text": "a. Thời hiệu xử lý bồi thường thiệt hại là 06 tháng kể từ ngày xảy ra vụ việc.",
        },
    ]

    remapped = remap_answer_citations(answer, citations)
    assert "[S2]" in remapped
    assert "[S1]" not in remapped
