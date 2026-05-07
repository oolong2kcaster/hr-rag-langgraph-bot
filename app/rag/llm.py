from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from openai import OpenAI

from app.config import Settings


class OpenAIClients:
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Set it in .env before ingestion or asking questions."
            )
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url.rstrip("/"),
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=cast(Any, messages),
            temperature=temperature,
        )
        return response.choices[0].message.content or ""


def batched(items: list[str], batch_size: int = 64) -> Iterable[list[str]]:
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]
