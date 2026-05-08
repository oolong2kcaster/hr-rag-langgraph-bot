from functools import lru_cache
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_chat_api_key: str | None = Field(default=None, alias="OPENAI_CHAT_API_KEY")
    openai_embedding_api_key: str | None = Field(
        default=None, alias="OPENAI_EMBEDDING_API_KEY"
    )
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")
    openai_chat_base_url: str | None = Field(default=None, alias="OPENAI_CHAT_BASE_URL")
    openai_embedding_base_url: str | None = Field(
        default=None, alias="OPENAI_EMBEDDING_BASE_URL"
    )
    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="hr_documents", alias="QDRANT_COLLECTION")

    data_dir: Path = Field(default=Path("data/raw"), alias="DATA_DIR")
    processed_dir: Path = Field(default=Path("data/processed"), alias="PROCESSED_DIR")
    log_dir: Path = Field(default=Path("logs"), alias="LOG_DIR")

    ocr_enabled: bool = Field(default=True, alias="OCR_ENABLED")
    ocr_lang: str = Field(default="vie+eng", alias="OCR_LANG")
    chunk_size: int = Field(default=900, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=160, alias="CHUNK_OVERLAP")

    retrieval_top_k: int = Field(default=6, alias="RETRIEVAL_TOP_K")
    semantic_candidates: int = Field(default=18, alias="SEMANTIC_CANDIDATES")
    retrieval_neighbor_window: int = Field(default=1, alias="RETRIEVAL_NEIGHBOR_WINDOW")
    max_context_chars: int = Field(default=9000, alias="MAX_CONTEXT_CHARS")
    min_relevance_score: float = Field(default=0.20, alias="MIN_RELEVANCE_SCORE")

    slack_bot_token: str | None = Field(default=None, alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str | None = Field(default=None, alias="SLACK_SIGNING_SECRET")
    slack_app_token: str | None = Field(default=None, alias="SLACK_APP_TOKEN")

    @model_validator(mode="after")
    def validate_openai_mode(self) -> "Settings":
        fields = (
            "openai_api_key",
            "openai_chat_api_key",
            "openai_embedding_api_key",
            "openai_base_url",
            "openai_chat_base_url",
            "openai_embedding_base_url",
        )
        for field_name in fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                normalized = value.strip() or None
                setattr(self, field_name, normalized)

        has_mode_a_values = bool(self.openai_base_url or self.openai_api_key)
        has_split_values = any(
            (
                self.openai_chat_base_url,
                self.openai_embedding_base_url,
                self.openai_chat_api_key,
                self.openai_embedding_api_key,
            )
        )

        if has_mode_a_values and has_split_values:
            raise ValueError(
                "Use exactly one OpenAI mode: Mode A (OPENAI_BASE_URL + OPENAI_API_KEY) or Mode B (OPENAI_CHAT_*/OPENAI_EMBEDDING_*)."
            )

        if not has_split_values:
            if not self.openai_base_url or not self.openai_api_key:
                raise ValueError("Mode A requires OPENAI_BASE_URL and OPENAI_API_KEY.")
            return self

        if not (
            self.openai_chat_base_url
            and self.openai_embedding_base_url
            and self.openai_chat_api_key
            and self.openai_embedding_api_key
        ):
            raise ValueError(
                "Mode B requires OPENAI_CHAT_BASE_URL, OPENAI_EMBEDDING_BASE_URL, OPENAI_CHAT_API_KEY, and OPENAI_EMBEDDING_API_KEY."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
