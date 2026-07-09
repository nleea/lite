"""Embedding provider wrapper.

Embeddings can come from a local Ollama model or from OpenAI (Anthropic has no
embeddings API). The provider is chosen with LLM_PROVIDER. LangChain orchestrates
whichever backend is selected.
"""

from __future__ import annotations

from functools import lru_cache

from app.config import settings


class EmbeddingsUnavailable(RuntimeError):
    """Raised when no embedding provider is configured."""


@lru_cache(maxsize=1)
def _client():
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        # The model determines the vector size (nomic-embed-text = 768);
        # keep EMBEDDING_DIMENSIONS in sync with the pgvector column.
        return OllamaEmbeddings(
            model=settings.ollama_embed_model,
            base_url=settings.ollama_base_url,
        )

    if provider == "openai":
        if not settings.openai_api_key:
            raise EmbeddingsUnavailable("OPENAI_API_KEY is not set")
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            api_key=settings.openai_api_key,
        )

    raise EmbeddingsUnavailable(f"No embedding provider for LLM_PROVIDER={provider!r}")


def embed_text(text: str) -> list[float]:
    """Embed a single document/query into a vector."""
    return _client().embed_query(text)


def build_document(name: str, characteristics: str, company_name: str) -> str:
    """The text that becomes the embedding (numbers stay out — they're metadata)."""
    return f"Product: {name}. Characteristics: {characteristics}. Company: {company_name}."
