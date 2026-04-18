"""Configuración global del sistema cargada desde .env."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── LangFuse ──────────────────────────────────────────────
    langfuse_public_key: str = "pk-test"
    langfuse_secret_key: str = "sk-test"
    langfuse_host: str = "https://cloud.langfuse.com"

    # ── LLM ───────────────────────────────────────────────────
    llm_provider: str = "ollama"          # ollama | openai | mock
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.3"
    openai_model: str = "gpt-4o"

    # ── Vector DB ─────────────────────────────────────────────
    chroma_path: str = "./data/chroma"

    # ── Postgres ──────────────────────────────────────────────
    postgres_url: str = "postgresql://rupestre:rupestre@localhost:5432/rupestre_db"

    # ── MinIO ─────────────────────────────────────────────────
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "rupestre-media"

    # ── Telegram ──────────────────────────────────────────────
    telegram_bot_token: str = ""

    # ── API ───────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
