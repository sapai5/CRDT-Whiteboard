"""
app/middleware/auth_middleware.py — Auth Service
─────────────────────────────────────────────────
Dependency used by protected routes to extract and forward
the bearer token from the Authorization header.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

async def require_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extract a Bearer token from the Authorization header using FastAPI's native HTTPBearer.
    This natively binds to Swagger UI's "Authorize" button and auto-extracts the token.
    """
    token = credentials.credentials
    
    # the format checker
    if token.count(".") != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Malformed token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
