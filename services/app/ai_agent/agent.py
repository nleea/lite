"""Tool-calling agent over the product catalogue.

The LLM (local via Ollama, or cloud) decides which tools to call: semantic
search, listing companies, counting/summarizing inventory, or emailing the
inventory PDF. A guardrail keeps it from inventing data. If tool-calling fails
(e.g. a model that can't call tools), it falls back to a single-shot RAG answer.
"""

from __future__ import annotations

import logging

import httpx

from app.ai_agent.retrieval import format_products, retrieve
from app.config import settings
from app.db import SessionLocal

logger = logging.getLogger(__name__)

# Errors meaning the LLM provider is unreachable (Ollama down, network, etc.).
# Ollama's client raises the builtin ConnectionError; httpx raises ConnectError.
_UNAVAILABLE_ERRORS = (ConnectionError, httpx.HTTPError)
_UNAVAILABLE_MESSAGE = (
    "The language model provider is unavailable. "
    "Check that the configured LLM (e.g. Ollama) is running and reachable."
)


class LLMUnavailableError(RuntimeError):
    """The configured LLM provider could not be reached.

    Subclasses RuntimeError so the router maps it to HTTP 503.
    """


SYSTEM_PROMPT = (
    "You are an assistant for a product-inventory application. "
    "Use the available tools to answer questions about companies, products, "
    "prices and inventory, and to email the inventory PDF when asked. "
    "Base every answer strictly on tool results — never invent products, "
    "prices, companies, or confirmations. If nothing matches, say so."
)


def answer(
    question: str,
    *,
    company_id: str | None = None,
    max_price_usd: float | None = None,
) -> dict:
    """Run the tool-calling agent and return the answer + which tools it used."""
    hint = ""
    if company_id:
        hint += f" (restrict to company NIT {company_id})"
    if max_price_usd is not None:
        hint += f" (maximum USD price {max_price_usd})"
    user_message = f"{question}{hint}"

    try:
        return _tool_calling_answer(user_message)
    except _UNAVAILABLE_ERRORS as exc:
        # Provider is down — the RAG fallback would hit the same wall, so bail out.
        raise LLMUnavailableError(_UNAVAILABLE_MESSAGE) from exc
    except Exception:
        logger.exception("Tool-calling agent failed; falling back to simple RAG")

    try:
        return _simple_answer(user_message)
    except _UNAVAILABLE_ERRORS as exc:
        raise LLMUnavailableError(_UNAVAILABLE_MESSAGE) from exc


def _tool_calling_answer(user_message: str) -> dict:
    """Primary path: let the LLM drive the tools."""
    from langgraph.prebuilt import create_react_agent

    from app.ai_agent.tools import TOOLS

    executor = create_react_agent(_chat_model(), TOOLS, prompt=SYSTEM_PROMPT)
    result = executor.invoke({"messages": [("user", user_message)]})
    messages = result["messages"]
    tools_used = [
        call["name"]
        for message in messages
        for call in (getattr(message, "tool_calls", None) or [])
    ]
    return {
        "answer": messages[-1].content,
        "tools_used": tools_used,
        "sources": [],
    }


def _simple_answer(question: str) -> dict:
    """Fallback: one retrieval + one generation, no tools."""
    with SessionLocal() as session:
        rows = retrieve(session, question)
        if not rows:
            return {"answer": "I found no matching products.", "tools_used": [], "sources": []}
        context = format_products(rows)
        prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        response = _chat_model().invoke(prompt)
        return {
            "answer": getattr(response, "content", str(response)),
            "tools_used": ["search_products"],
            "sources": [{"code": r.code, "product_id": r.product_id} for r in rows],
        }


def _chat_model():
    """Build the chat model for the configured provider (LLM_PROVIDER)."""
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_chat_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )
    if provider == "anthropic" and settings.anthropic_api_key:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.chat_model, api_key=settings.anthropic_api_key, temperature=0
        )
    if provider == "openai" and settings.openai_api_key:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o-mini", api_key=settings.openai_api_key, temperature=0)

    raise RuntimeError(
        f"No chat model configured for LLM_PROVIDER={provider!r} "
        "(set the matching key or run Ollama)"
    )
