"""
Slack bot scaffold for Phase 2.

Phase 1 runs from terminal only:
    python -m app.main ask "..."

When you are ready for Slack integration:
1. Set SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, SLACK_APP_TOKEN in .env
2. Add bot scopes: app_mentions:read, chat:write, im:history, im:read
3. Run this module with Socket Mode enabled.
"""

from __future__ import annotations

import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.config import get_settings
from app.rag.graph import HRRAGGraph
from app.utils.logging import configure_logging

logger = logging.getLogger(__name__)


def build_slack_app() -> App:
    settings = get_settings()
    configure_logging(settings.log_dir)
    if not settings.slack_bot_token or not settings.slack_signing_secret:
        raise RuntimeError("Missing SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET")

    slack_app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)
    rag_graph = HRRAGGraph(settings)

    @slack_app.event("app_mention")
    def handle_app_mention(event, say):  # noqa: ANN001
        text = event.get("text", "")
        result = rag_graph.invoke(text)
        answer = result.get("answer", "Tôi chưa tìm thấy thông tin trong tài liệu đã nạp.")
        sources = result.get("citations", [])[:3]
        source_lines = [
            f"• [{s['label']}] {s['source_name']} - page {s['page']} - chunk {s['chunk_index']}"
            for s in sources
        ]
        say(answer + ("\n\n*Nguồn:*\n" + "\n".join(source_lines) if source_lines else ""))

    return slack_app


def main() -> None:
    settings = get_settings()
    slack_app = build_slack_app()
    if not settings.slack_app_token:
        raise RuntimeError("Missing SLACK_APP_TOKEN for Socket Mode")
    SocketModeHandler(slack_app, settings.slack_app_token).start()


if __name__ == "__main__":
    main()
