"""JWT validation. FastAPI validates the token Django issued — it never mints one.

Validation is offline: the signature is checked with the shared key, and the
`rol` claim drives authorization without ever calling Django.
"""

from __future__ import annotations

from dataclasses import dataclass

import jwt
from domain.rules import can_use_ai_agent
from domain.value_objects import Role
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class Principal:
    """The authenticated caller, derived from JWT claims."""

    subject: str
    role: Role
    token_type: str


def _decode(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_signing_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def current_principal(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Principal:
    claims = _decode(credentials.credentials)
    raw_role = claims.get("rol", "external")
    try:
        role = Role.parse(raw_role)
    except Exception:
        role = Role.EXTERNAL
    return Principal(
        subject=str(claims.get("sub", "")),
        role=role,
        token_type=str(claims.get("type", "user")),
    )


def require_admin(principal: Principal = Depends(current_principal)) -> Principal:
    """Guard for admin-only endpoints (e.g. the AI agent)."""
    if not can_use_ai_agent(principal.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return principal
