from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Optional

import typer
from langchain_core._api.deprecation import LangChainPendingDeprecationWarning
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.config import get_settings
from app.ingestion.indexer import ingest_path
from app.ingestion.validator import validate_index
from app.rag.agents import list_document_agents
from app.rag.graph import HRRAGGraph
from app.storage.qdrant_store import QdrantVectorStore
from app.utils.logging import configure_logging

warnings.filterwarnings(
    "ignore",
    message="The default value of `allowed_objects` will change in a future version.*",
    category=LangChainPendingDeprecationWarning,
)

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


def bootstrap():
    settings = get_settings()
    configure_logging(settings.log_dir)
    return settings


@app.command()
def ingest(
    path: Path = typer.Option(
        Path("data/raw"), "--path", "-p", help="File or folder to ingest"
    ),
):
    """Load documents, OCR scanned PDFs if needed, chunk, embed, and upsert into Qdrant."""
    settings = bootstrap()
    report = ingest_path(path, settings)
    console.print_json(json.dumps(report, ensure_ascii=False))


@app.command()
def validate(
    query: Optional[str] = typer.Option(
        "người lao động được nghỉ hằng năm bao nhiêu ngày",
        "--query",
        "-q",
        help="Optional retrieval test query",
    ),
):
    """Validate indexed data and optionally run a retrieval smoke test."""
    settings = bootstrap()
    report = validate_index(settings, query=query)
    if not report["ok"]:
        raise typer.Exit(code=1)


@app.command()
def agents():
    """List document-agents. Phase 1 maps every source document to one agent_id."""
    settings = bootstrap()
    rows = list_document_agents(settings)
    table = Table(title="Document agents")
    table.add_column("Agent ID")
    table.add_column("Sources")
    table.add_column("Pages", justify="right")
    table.add_column("Chunks", justify="right")
    for row in rows:
        table.add_row(
            row["agent_id"],
            ", ".join(row["sources"]),
            str(row["page_count"]),
            str(row["chunks"]),
        )
    console.print(table)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the HR RAG bot"),
    agent: Optional[str] = typer.Option(
        None, "--agent", "-a", help="Limit retrieval to one document-agent"
    ),
    domain: Optional[str] = typer.Option(
        None, "--domain", "-d", help="Optional domain hint: policy | tax_2026"
    ),
    raw: bool = typer.Option(False, "--raw", help="Print raw JSON state"),
):
    """Ask from terminal using production-style LangGraph RAG flow."""
    settings = bootstrap()
    graph = HRRAGGraph(settings)
    result = graph.invoke(question=question, agent_id=agent, domain_hint=domain)

    if raw:
        console.print_json(json.dumps(result, ensure_ascii=False, default=str))
        return

    console.print(
        Panel(result.get("answer") or "", title="AI Answer", border_style="green")
    )

    citations = result.get("citations", [])
    if citations:
        table = Table(title="Evidence / Sources")
        table.add_column("Label")
        table.add_column("Source")
        table.add_column("Page", justify="right")
        table.add_column("Chunk", justify="right")
        table.add_column("Score", justify="right")
        table.add_column("Excerpt")
        for c in citations:
            table.add_row(
                c.get("label", ""),
                c.get("source_name", ""),
                str(c.get("page", "")),
                str(c.get("chunk_index", "")),
                str(c.get("score", "")),
                c.get("excerpt", ""),
            )
        console.print(table)
    else:
        console.print("[yellow]No evidence found from indexed documents.[/yellow]")

    verification = result.get("verification", {})
    console.print(
        Panel(
            json.dumps(verification, ensure_ascii=False, indent=2),
            title="Verification",
            border_style="blue",
        )
    )


@app.command("reset-index")
def reset_index(
    yes: bool = typer.Option(False, "--yes", help="Confirm deletion"),
):
    """Delete Qdrant collection. Does not delete raw documents."""
    if not yes:
        console.print("Use --yes to confirm.")
        raise typer.Exit(code=1)
    settings = bootstrap()
    store = QdrantVectorStore(settings)
    store.reset()
    console.print("[green]Index reset completed.[/green]")


if __name__ == "__main__":
    app()
