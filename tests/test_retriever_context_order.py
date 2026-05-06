from types import SimpleNamespace

from app.rag.retriever import HybridRetriever


def _make_doc(chunk_index: int, page: int, score: float = 0.0) -> dict:
    return {
        "id": f"id-{chunk_index}",
        "source_name": "policy.pdf",
        "source_path": "/docs/policy.pdf",
        "agent_id": "policy",
        "page": page,
        "chunk_index": chunk_index,
        "text": f"chunk {chunk_index}",
        "score": score,
        "score_breakdown": {"semantic": score, "lexical": 0.0},
    }


def test_expand_neighbors_and_sort_for_context():
    retriever = HybridRetriever.__new__(HybridRetriever)
    retriever.settings = SimpleNamespace(retrieval_neighbor_window=1)

    corpus = [
        _make_doc(91, 30),
        _make_doc(92, 30),
        _make_doc(93, 31),
        _make_doc(94, 31),
        _make_doc(95, 31),
    ]
    # Simulate semantic/hybrid top chunks coming in discontinuous order.
    top_docs = [
        _make_doc(94, 31, score=0.93),
        _make_doc(93, 31, score=0.91),
        _make_doc(91, 30, score=0.90),
    ]

    expanded = retriever._expand_with_neighbors(top_docs=top_docs, corpus=corpus)
    ordered = retriever._sort_for_context(expanded)

    assert [d["chunk_index"] for d in ordered] == [91, 92, 93, 94, 95]


def test_neighbor_expansion_respects_source_boundary():
    retriever = HybridRetriever.__new__(HybridRetriever)
    retriever.settings = SimpleNamespace(retrieval_neighbor_window=1)

    top_docs = [_make_doc(10, 2, score=0.88)]
    corpus = [
        _make_doc(9, 2),
        _make_doc(10, 2),
        _make_doc(11, 3),
        {
            **_make_doc(11, 5),
            "id": "other-11",
            "source_name": "other.pdf",
            "source_path": "/docs/other.pdf",
        },
    ]

    expanded = retriever._expand_with_neighbors(top_docs=top_docs, corpus=corpus)
    ids = {d["id"] for d in expanded}

    assert "id-9" in ids
    assert "id-11" in ids
    assert "other-11" not in ids
