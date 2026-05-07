from __future__ import annotations

from rich.console import Console
from rich.table import Table

from app.config import Settings
from app.rag.retriever import HybridRetriever
from app.storage.qdrant_store import QdrantVectorStore

console = Console()


def validate_index(settings: Settings, query: str | None = None) -> dict:
    store = QdrantVectorStore(settings)
    count = store.count()

    report = {
        "collection": settings.qdrant_collection,
        "count": count,
        "ok": count > 0,
        "sample_query": query,
        "sample_results": [],
    }

    console.print(f"Collection: [bold]{settings.qdrant_collection}[/bold]")
    console.print(f"Indexed chunks: [bold]{count}[/bold]")

    if count <= 0:
        console.print("[red]No chunks found. Run: make ingest DOCS=data/raw[/red]")
        return report

    sample = store.scroll_payloads(limit=5)
    table = Table(title="Payload sanity check")
    table.add_column("Source")
    table.add_column("Page", justify="right")
    table.add_column("Chunk", justify="right")
    table.add_column("Agent")
    table.add_column("Domain")
    table.add_column("Excerpt")
    for item in sample:
        table.add_row(
            str(item.get("source_name")),
            str(item.get("page")),
            str(item.get("chunk_index")),
            str(item.get("agent_id")),
            str(item.get("domain")),
            (item.get("text") or "")[:100].replace("\n", " "),
        )
    console.print(table)

    if query:
        retriever = HybridRetriever(settings)
        results = retriever.retrieve(query)
        report["sample_results"] = results
        result_table = Table(title=f"Retrieval test: {query}")
        result_table.add_column("Score", justify="right")
        result_table.add_column("Source")
        result_table.add_column("Page", justify="right")
        result_table.add_column("Chunk", justify="right")
        result_table.add_column("Excerpt")
        for item in results:
            result_table.add_row(
                f"{float(item.get('score', 0.0)):.4f}",
                str(item.get("source_name")),
                str(item.get("page")),
                str(item.get("chunk_index")),
                (item.get("text") or "")[:140].replace("\n", " "),
            )
        console.print(result_table)

    return report
