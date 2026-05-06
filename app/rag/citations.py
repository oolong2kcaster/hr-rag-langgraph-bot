from __future__ import annotations

import re


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
                "context_text": excerpt,
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


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\wÀ-ỹ]+", (text or "").lower(), flags=re.UNICODE))


def _best_label_for_sentence(sentence: str, citations: list[dict]) -> str | None:
    sentence_tokens = _tokens(re.sub(r"\[S\d+\]", " ", sentence))
    if not sentence_tokens:
        return None

    best_label: str | None = None
    best_score = 0.0
    for citation in citations:
        source_text = str(citation.get("context_text") or citation.get("excerpt") or "")
        source_tokens = _tokens(source_text)
        if not source_tokens:
            continue
        overlap = sentence_tokens.intersection(source_tokens)
        if not overlap:
            continue
        score = len(overlap) / max(len(sentence_tokens), 1)
        if score > best_score:
            best_score = score
            best_label = str(citation.get("label"))
    return best_label


def remap_answer_citations(answer: str, citations: list[dict]) -> str:
    if not answer or not citations:
        return answer

    remapped_lines: list[str] = []
    for line in answer.splitlines(keepends=True):
        labels = re.findall(r"\[(S\d+)\]", line)
        if not labels:
            remapped_lines.append(line)
            continue
        best = _best_label_for_sentence(line, citations)
        if not best:
            remapped_lines.append(line)
            continue
        replaced = re.sub(r"(?:\s*\[S\d+\])+", f" [{best}]", line)
        remapped_lines.append(replaced)
    return "".join(remapped_lines)
