"""
app/middleware/auth_middleware.py — Persistence Service
────────────────────────────────────────────────────────
Same pattern as Room Service — validates Bearer token against Auth Service.
Internal service-to-service calls (from CRDT Sync) should use a
shared service secret header instead of a user JWT.
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
    """Validate Bearer token via Auth Service."""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid header.")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{settings.auth_service_url}/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service unreachable.")

    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    data = resp.json()
    return CurrentUser(user_id=UUID(data["user_id"]), email=data["email"], display_name=data["display_name"])
