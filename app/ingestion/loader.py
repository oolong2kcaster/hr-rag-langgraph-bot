from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Iterable

from PIL import Image
import fitz  # type: ignore
import pytesseract  # type: ignore
from slugify import slugify

from app.ingestion.models import RawPage

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def discover_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in SUPPORTED_EXTENSIONS else []
    return sorted(
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def agent_id_for_file(path: Path) -> str:
    return slugify(path.stem, lowercase=True)[:80] or "document-agent"


def load_pages(
    path: Path, ocr_enabled: bool = True, ocr_lang: str = "vie+eng"
) -> list[RawPage]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return list(_load_pdf_pages(path, ocr_enabled=ocr_enabled, ocr_lang=ocr_lang))
    if ext in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return [RawPage(str(path), path.name, 1, text)]
    raise ValueError(f"Unsupported file type: {path}")


def _load_pdf_pages(path: Path, ocr_enabled: bool, ocr_lang: str) -> Iterable[RawPage]:
    doc = fitz.open(path)
    logger.info("Loading PDF %s with %s pages", path, doc.page_count)

    for index, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()

        # Scanned PDFs often have no embedded text. OCR only that page when needed.
        if ocr_enabled and len(text) < 40:
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                text = pytesseract.image_to_string(image, lang=ocr_lang).strip()
                logger.info(
                    "OCR page %s/%s from %s: %s chars",
                    index,
                    doc.page_count,
                    path.name,
                    len(text),
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("OCR failed for %s page %s: %s", path, index, exc)
                text = ""

        yield RawPage(str(path), path.name, index, text)
