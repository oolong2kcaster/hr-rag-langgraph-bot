from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from openai import OpenAI

from app.config import Settings


class OpenAIClients:
    def __init__(self, settings: Settings):
        chat_api_key = settings.openai_chat_api_key or settings.openai_api_key
        embedding_api_key = settings.openai_embedding_api_key or settings.openai_api_key
        if not chat_api_key:
            raise RuntimeError(
                "Missing chat API key. Set OPENAI_CHAT_API_KEY (or OPENAI_API_KEY as fallback) in .env."
            )
        if not embedding_api_key:
            raise RuntimeError(
                "Missing embedding API key. Set OPENAI_EMBEDDING_API_KEY (or OPENAI_API_KEY as fallback) in .env."
            )
        self.settings = settings
        chat_base_url = settings.openai_chat_base_url or settings.openai_base_url
        embedding_base_url = (
            settings.openai_embedding_base_url or settings.openai_base_url
        )
        if not chat_base_url:
            raise RuntimeError(
                "Missing chat base URL. Set OPENAI_CHAT_BASE_URL (or OPENAI_BASE_URL as fallback) in .env."
            )
        if not embedding_base_url:
            raise RuntimeError(
                "Missing embedding base URL. Set OPENAI_EMBEDDING_BASE_URL (or OPENAI_BASE_URL as fallback) in .env."
            )
        self.chat_client = OpenAI(
            api_key=chat_api_key,
            base_url=chat_base_url.rstrip("/"),
        )
        self.embedding_client = OpenAI(
            api_key=embedding_api_key,
            base_url=embedding_base_url.rstrip("/"),
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.embedding_client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        response = self.chat_client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=cast(Any, messages),
            temperature=temperature,
        )
        return response.choices[0].message.content or ""


def batched(items: list[str], batch_size: int = 64) -> Iterable[list[str]]:
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]
