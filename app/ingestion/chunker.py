from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.ingestion.loader import agent_id_for_file, sha256_file
from app.ingestion.models import DocumentChunk, RawPage

LEGAL_SECTION_PATTERN = re.compile(
    r"^\s*(?:điều\s+\d+(?:[./]\d+)*|khoản\s+\d+(?:[./]\d+)*|[a-zA-Z]\.)\s*",
    flags=re.IGNORECASE,
)


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_legal_sections(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    marker_count = sum(1 for line in lines if LEGAL_SECTION_PATTERN.match(line))
    if marker_count < 2:
        return [text]

    sections: list[str] = []
    current: list[str] = []
    for line in lines:
        if LEGAL_SECTION_PATTERN.match(line) and current:
            sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [section for section in sections if section]


def _split_section_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            flush()
            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                window = paragraph[start:end]
                # Prefer ending on a sentence boundary when possible.
                boundary = max(
                    window.rfind(". "), window.rfind("; "), window.rfind("\n")
                )
                if boundary > int(chunk_size * 0.55) and end < len(paragraph):
                    end = start + boundary + 1
                chunks.append(paragraph[start:end].strip())
                if end >= len(paragraph):
                    break
                start = max(0, end - chunk_overlap)
            continue

        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
        else:
            flush()
            current = paragraph

    flush()

    if chunk_overlap > 0 and len(chunks) > 1:
        with_overlap: list[str] = []
        previous_tail = ""
        for chunk in chunks:
            merged = f"{previous_tail}\n{chunk}".strip() if previous_tail else chunk
            with_overlap.append(merged)
            previous_tail = chunk[-chunk_overlap:]
        chunks = with_overlap

    return [c for c in chunks if c.strip()]


def split_text(text: str, chunk_size: int = 900, chunk_overlap: int = 160) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    sections = _split_legal_sections(text)
    chunks: list[str] = []
    for section in sections:
        chunks.extend(
            _split_section_text(
                section, chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
        )
    return [c for c in chunks if c.strip()]


def chunks_from_pages(
    pages: list[RawPage], chunk_size: int, chunk_overlap: int
) -> list[DocumentChunk]:
    result: list[DocumentChunk] = []
    if not pages:
        return result

    source_path = Path(pages[0].source_path)
    doc_sha = sha256_file(source_path)
    agent_id = agent_id_for_file(source_path)

    global_index = 0
    for page in pages:
        for text in split_text(
            page.text, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        ):
            stable = f"{doc_sha}:{page.page}:{global_index}:{text[:80]}"
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, stable))
            result.append(
                DocumentChunk(
                    id=chunk_id,
                    text=text,
                    source_path=page.source_path,
                    source_name=page.source_name,
                    page=page.page,
                    chunk_index=global_index,
                    agent_id=agent_id,
                    doc_sha256=doc_sha,
                )
            )
            global_index += 1
    return result
