"""AI agent endpoints (admin-only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.ai_agent import agent
from app.auth import Principal, require_admin

router = APIRouter(prefix="/agent", tags=["ai-agent"])


class ChatRequest(BaseModel):
    question: str
    company_id: str | None = None
    max_price_usd: float | None = None


class ChatResponse(BaseModel):
    answer: str
    tools_used: list[str] = []
    sources: list[dict] = []


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    _admin: Principal = Depends(require_admin),
) -> ChatResponse:
    try:
        result = agent.answer(
            payload.question,
            company_id=payload.company_id,
            max_price_usd=payload.max_price_usd,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(**result)
