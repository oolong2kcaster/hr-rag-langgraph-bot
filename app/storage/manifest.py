from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class IngestManifest:
    def __init__(self, processed_dir: Path):
        self.path = processed_dir / "ingest_manifest.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict[str, Any]) -> None:
        record = {**record, "created_at": datetime.now(timezone.utc).isoformat()}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records
