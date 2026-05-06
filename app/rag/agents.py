from __future__ import annotations

from collections import defaultdict

from app.config import Settings
from app.storage.qdrant_store import QdrantVectorStore


def list_document_agents(settings: Settings) -> list[dict]:
    store = QdrantVectorStore(settings)
    payloads = store.scroll_payloads(limit=10000)
    agents: dict[str, dict] = defaultdict(
        lambda: {"chunks": 0, "sources": set(), "pages": set()}
    )

    for payload in payloads:
        agent_id = payload.get("agent_id") or "unknown"
        agents[agent_id]["agent_id"] = agent_id
        agents[agent_id]["chunks"] += 1
        agents[agent_id]["sources"].add(payload.get("source_name"))
        if payload.get("page"):
            agents[agent_id]["pages"].add(payload.get("page"))

    result = []
    for agent in agents.values():
        result.append(
            {
                "agent_id": agent["agent_id"],
                "chunks": agent["chunks"],
                "sources": sorted(s for s in agent["sources"] if s),
                "page_count": len(agent["pages"]),
            }
        )
    return sorted(result, key=lambda a: a["agent_id"])
