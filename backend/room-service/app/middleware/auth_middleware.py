"""
app/middleware/auth_middleware.py — Room Service
─────────────────────────────────────────────────
Validates incoming Bearer tokens by calling the Auth Service's
/auth/validate endpoint. Injects user claims into route dependencies.
"""

from dataclasses import dataclass
from uuid import UUID

import httpx
from fastapi import Depends, Header, HTTPException, status

from app.config import settings


@dataclass
class CurrentUser:
    user_id: UUID
    email: str
    display_name: str


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
) -> CurrentUser:
    """
    FastAPI dependency — validates the Bearer token against the Auth Service
    and returns the embedded user claims.

    TODO:
      - Add a short in-memory cache (or Redis) to avoid hitting Auth Service
        on every request (respect token TTL for cache expiry).
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header.",
        )

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{settings.auth_service_url}/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth Service unreachable.",
            )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    data = resp.json()
    return CurrentUser(
        user_id=UUID(data["user_id"]),
        email=data["email"],
        display_name=data["display_name"],
    )
