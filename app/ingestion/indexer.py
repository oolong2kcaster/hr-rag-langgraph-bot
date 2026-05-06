from __future__ import annotations

import json
import logging
from pathlib import Path

from rich.console import Console
from rich.table import Table

from app.config import Settings
from app.ingestion.chunker import chunks_from_pages
from app.ingestion.loader import discover_files, load_pages, sha256_file
from app.rag.llm import OpenAIClients, batched
from app.storage.manifest import IngestManifest
from app.storage.qdrant_store import QdrantVectorStore

logger = logging.getLogger(__name__)
console = Console()


def ingest_path(path: Path, settings: Settings) -> dict:
    files = discover_files(path)
    if not files:
        raise FileNotFoundError(f"No supported files found in {path}. Supported: pdf, txt, md")

    llm = OpenAIClients(settings)
    store = QdrantVectorStore(settings)
    manifest = IngestManifest(settings.processed_dir)

    report = {
        "input_path": str(path),
        "files": [],
        "total_chunks": 0,
        "total_pages": 0,
    }

    table = Table(title="Ingestion report")
    table.add_column("File")
    table.add_column("Pages", justify="right")
    table.add_column("Chunks", justify="right")
    table.add_column("Agent ID")
    table.add_column("Status")

    for file in files:
        try:
            pages = load_pages(file, ocr_enabled=settings.ocr_enabled, ocr_lang=settings.ocr_lang)
            chunks = chunks_from_pages(pages, settings.chunk_size, settings.chunk_overlap)
            if not chunks:
                status = "skipped: no text extracted"
                table.add_row(file.name, str(len(pages)), "0", "-", status)
                logger.warning("No chunks extracted from %s", file)
                continue

            all_vectors: list[list[float]] = []
            for batch in batched([c.text for c in chunks], batch_size=64):
                all_vectors.extend(llm.embed(batch))

            store.upsert_chunks(chunks, all_vectors)

            doc_record = {
                "file": str(file),
                "file_name": file.name,
                "sha256": sha256_file(file),
                "pages": len(pages),
                "chunks": len(chunks),
                "agent_id": chunks[0].agent_id,
                "status": "ok",
            }
            manifest.append(doc_record)
            report["files"].append(doc_record)
            report["total_chunks"] += len(chunks)
            report["total_pages"] += len(pages)
            table.add_row(file.name, str(len(pages)), str(len(chunks)), chunks[0].agent_id, "ok")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ingestion failed for %s", file)
            doc_record = {
                "file": str(file),
                "file_name": file.name,
                "sha256": sha256_file(file),
                "pages": 0,
                "chunks": 0,
                "agent_id": "-",
                "status": f"error: {exc}",
            }
            report["files"].append(doc_record)
            table.add_row(file.name, "0", "0", "-", f"error: {exc}")

    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    report_path = settings.processed_dir / "ingest_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    console.print(table)
    console.print(f"[green]Saved report:[/green] {report_path}")
    console.print(f"[green]Qdrant collection count:[/green] {store.count()}")
    return report
