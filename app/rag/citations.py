from __future__ import annotations


def source_label(index: int) -> str:
    return f"S{index}"


def format_context(docs: list[dict], max_chars: int) -> tuple[str, list[dict]]:
    parts: list[str] = []
    citations: list[dict] = []
    total = 0

    for i, doc in enumerate(docs, start=1):
        label = source_label(i)
        text = (doc.get("text") or "").strip()
        if not text:
            continue
        excerpt = text[:1200]
        block = (
            f"[{label}] source={doc.get('source_name')} | page={doc.get('page')} | "
            f"chunk={doc.get('chunk_index')} | agent={doc.get('agent_id')}\n"
            f"{excerpt}"
        )
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
        citations.append(
            {
                "label": label,
                "source_name": doc.get("source_name"),
                "source_path": doc.get("source_path"),
                "page": doc.get("page"),
                "chunk_index": doc.get("chunk_index"),
                "agent_id": doc.get("agent_id"),
                "score": round(float(doc.get("score", 0.0)), 4),
                "excerpt": text[:360].replace("\n", " "),
            }
        )
    return "\n\n---\n\n".join(parts), citations


def ensure_citation_note(answer: str, citations: list[dict]) -> str:
    if not citations:
        return answer
    if any(f"[{c['label']}]" in answer for c in citations):
        return answer
    labels = ", ".join(f"[{c['label']}]" for c in citations[:3])
    return f"{answer}\n\nNguồn tham khảo chính: {labels}."
