from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")

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
    max_context_chars: int = Field(default=9000, alias="MAX_CONTEXT_CHARS")
    min_relevance_score: float = Field(default=0.20, alias="MIN_RELEVANCE_SCORE")

    slack_bot_token: str | None = Field(default=None, alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str | None = Field(default=None, alias="SLACK_SIGNING_SECRET")
    slack_app_token: str | None = Field(default=None, alias="SLACK_APP_TOKEN")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
