from __future__ import annotations

from enum import StrEnum

from app.domains.base import DomainConfig


class Domain(StrEnum):
    POLICY = "policy"
    TAX_2026 = "tax_2026"
    UNKNOWN = "unknown"


DOMAIN_REGISTRY: dict[Domain, DomainConfig] = {
    Domain.POLICY: DomainConfig(
        name="Nội quy / nghỉ phép",
        retrieval_filter={"domain": Domain.POLICY.value},
        requires_evidence=True,
        requires_tools=False,
    ),
    Domain.TAX_2026: DomainConfig(
        name="Thuế TNCN 2026",
        retrieval_filter={"domain": Domain.TAX_2026.value},
        requires_evidence=True,
        requires_tools=True,
    ),
}
