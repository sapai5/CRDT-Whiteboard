"""
app/routes/auth.py — Auth Service
───────────────────────────────────
REST endpoints for authentication.
All handlers delegate to AuthService; no logic lives in routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.auth_middleware import require_bearer_token
from app.services.token_utils import decode_token, is_blocklisted
from jose import JWTError
from app.models.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UpdateProfileRequest,
    UserResponse,
    ValidateTokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
_svc = AuthService()


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(payload: RegisterRequest, db=Depends(get_db)) -> UserResponse:
    return await _svc.register(payload, db)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login and receive access + refresh tokens",
)
async def login(payload: LoginRequest, db=Depends(get_db)) -> TokenPair:
    return await _svc.login(payload, db)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Rotate a refresh token for a new token pair",
)
async def refresh(payload: RefreshRequest, db=Depends(get_db)) -> TokenPair:
    return await _svc.refresh(payload, db)


# ── Internal endpoint (called by other services) ──────────────────────────────

@router.get(
    "/validate",
    response_model=ValidateTokenResponse,
    summary="[Internal] Validate an access token and return claims",
)
async def validate_token(token: str = Depends(require_bearer_token)) -> ValidateTokenResponse:
    return await _svc.validate_token(token)


def get_current_user_id(token: str = Depends(require_bearer_token)) -> UUID:
    """Dependency to extract user_id from the validated bearer token."""
    try:
        claims = decode_token(token)
        jti = claims.get("jti")
        
        # Explicitly enforce the logout blocklist for internal routes!
        if jti and is_blocklisted(jti):
            raise ValueError("Token has been logged out")
            
        return UUID(claims["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ── Protected endpoints ───────────────────────────────────────────────────────

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate the current session",
)
async def logout(
    user_id: UUID = Depends(get_current_user_id),
    token: str = Depends(require_bearer_token),
    db: Session = Depends(get_db),
) -> None:
    await _svc.logout(user_id, token, db)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
)
async def get_profile(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> UserResponse:
    return await _svc.get_profile(user_id, db)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the authenticated user's profile",
)
async def update_profile(
    payload: UpdateProfileRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> UserResponse:
    return await _svc.update_profile(user_id, payload, db)


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the authenticated user's password",
)
async def change_password(
    payload: ChangePasswordRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    await _svc.change_password(user_id, payload.current_password, payload.new_password, db)
