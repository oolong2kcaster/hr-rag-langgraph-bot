from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class RawPage:
    source_path: str
    source_name: str
    page: int
    text: str


@dataclass
class DocumentChunk:
    id: str
    text: str
    source_path: str
    source_name: str
    page: int
    chunk_index: int
    agent_id: str
    doc_sha256: str

    def payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("id", None)
        return payload
