from __future__ import annotations

from app.domains.registry import Domain


def detect_domain_from_file(filename: str, text_sample: str = "") -> Domain:
    name = (filename or "").lower()
    sample = (text_sample or "").lower()

    if "noi_quy" in name or "nội quy" in sample or "lao động" in sample:
        return Domain.POLICY
    if "thue" in name or "thuế" in sample or "tncn" in sample:
        return Domain.TAX_2026
    return Domain.UNKNOWN
