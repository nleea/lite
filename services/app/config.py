"""Typed settings loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # JWT — MUST match the Django issuer's key/algorithm.
    jwt_signing_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    # Database (shared with Django; SQLAlchemy reads core tables + owns embeddings).
    postgres_db: str = "lite"
    postgres_user: str = "lite"
    postgres_password: str = "lite"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis event stream (consumer side).
    redis_host: str = "localhost"
    redis_port: int = 6379
    product_events_stream: str = "product-events"

    # AI provider selection: "ollama" (local), "openai", or "anthropic".
    llm_provider: str = "ollama"

    # Embedding vector size — MUST match the chosen embedding model and the
    # pgvector column. nomic-embed-text = 768; OpenAI text-embedding-3 = 1536.
    embedding_dimensions: int = 768

    # Ollama (local agent). From inside Docker, reach the host via
    # host.docker.internal; on the host directly use http://localhost:11434.
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_chat_model: str = "llama3.1"
    ollama_embed_model: str = "nomic-embed-text"

    # OpenAI / Anthropic (cloud fallback).
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "claude-sonnet-5"

    # Email (Resend).
    resend_api_key: str = ""
    email_from: str = "inventory@example.com"

    # Blockchain (local EVM anchoring of the inventory PDF hash).
    web3_rpc_url: str = "http://anvil:8545"
    web3_chain_id: int = 31337
    web3_private_key: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    solc_version: str = "0.8.24"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
