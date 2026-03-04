"""
app/middleware/auth_middleware.py — Auth Service
─────────────────────────────────────────────────
Dependency used by protected routes to extract and forward
the bearer token from the Authorization header.
"""

from fastapi import Header, HTTPException, status


async def require_bearer_token(
    authorization: str = Header(..., alias="Authorization"),
) -> str:
    """
    Extract a Bearer token from the Authorization header.

    TODO:
      - Optionally pre-validate format here before hitting AuthService
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header. Expected 'Bearer <token>'.",
        )
    return token
