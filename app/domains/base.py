from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DomainConfig:
    name: str
    retrieval_filter: dict[str, Any] = field(default_factory=dict)
    requires_evidence: bool = True
    requires_tools: bool = False
