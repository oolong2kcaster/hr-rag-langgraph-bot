from __future__ import annotations

import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from app.config import Settings
from app.ingestion.models import DocumentChunk

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection

    def ensure_collection(self, vector_size: int) -> None:
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection for c in collections)
        if exists:
            return

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=qm.VectorParams(
                size=vector_size, distance=qm.Distance.COSINE
            ),
        )
        logger.info(
            "Created Qdrant collection=%s vector_size=%s", self.collection, vector_size
        )

    def upsert_chunks(
        self, chunks: list[DocumentChunk], vectors: list[list[float]]
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors length mismatch")
        if not chunks:
            return
        self.ensure_collection(len(vectors[0]))

        points = [
            qm.PointStruct(
                id=chunk.id,
                vector=vector,
                payload={**chunk.payload(), "text": chunk.text},
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(collection_name=self.collection, points=points)
        logger.info(
            "Upserted %s chunks into collection=%s", len(points), self.collection
        )

    def count(self) -> int:
        try:
            response = self.client.count(collection_name=self.collection, exact=True)
            return int(response.count)
        except Exception:  # noqa: BLE001
            return 0

    def reset(self) -> None:
        collections = self.client.get_collections().collections
        if any(c.name == self.collection for c in collections):
            self.client.delete_collection(collection_name=self.collection)
            logger.warning("Deleted Qdrant collection=%s", self.collection)

    def scroll_payloads(
        self, limit: int = 5000, agent_id: str | None = None
    ) -> list[dict]:
        must: list[qm.Condition] = []
        if agent_id:
            must.append(
                qm.FieldCondition(key="agent_id", match=qm.MatchValue(value=agent_id))
            )
        scroll_filter = qm.Filter(must=must) if must else None

        points: list[dict] = []
        offset = None
        while True:
            batch, offset = self.client.scroll(
                collection_name=self.collection,
                scroll_filter=scroll_filter,
                limit=min(256, max(1, limit - len(points))),
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for point in batch:
                payload = dict(point.payload or {})
                payload["id"] = str(point.id)
                points.append(payload)
            if offset is None or len(points) >= limit:
                break
        return points

    def search(
        self,
        vector: list[float],
        limit: int,
        agent_id: str | None = None,
    ) -> list[dict]:
        must: list[qm.Condition] = []
        if agent_id:
            must.append(
                qm.FieldCondition(key="agent_id", match=qm.MatchValue(value=agent_id))
            )
        query_filter = qm.Filter(must=must) if must else None
        response = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        hits = response.points
        results: list[dict] = []
        for hit in hits:
            payload = dict(hit.payload or {})
            payload["id"] = str(hit.id)
            payload["semantic_score"] = float(hit.score or 0.0)
            results.append(payload)
        return results
