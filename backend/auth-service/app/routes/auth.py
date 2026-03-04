"""
app/routes/auth.py — Auth Service
───────────────────────────────────
REST endpoints for authentication.
All handlers delegate to AuthService; no logic lives in routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import require_bearer_token
from app.models.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
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
async def register(payload: RegisterRequest) -> UserResponse:
    return await _svc.register(payload)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login and receive access + refresh tokens",
)
async def login(payload: LoginRequest) -> TokenPair:
    return await _svc.login(payload)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Rotate a refresh token for a new token pair",
)
async def refresh(payload: RefreshRequest) -> TokenPair:
    return await _svc.refresh(payload)


# ── Internal endpoint (called by other services) ──────────────────────────────

@router.get(
    "/validate",
    response_model=ValidateTokenResponse,
    summary="[Internal] Validate an access token and return claims",
)
async def validate_token(token: str = Depends(require_bearer_token)) -> ValidateTokenResponse:
    return await _svc.validate_token(token)


# ── Protected endpoints ───────────────────────────────────────────────────────

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate the current session",
)
async def logout(token: str = Depends(require_bearer_token)) -> None:
    # TODO: extract user_id from validated token
    user_id: UUID = ...  # type: ignore[assignment]
    await _svc.logout(user_id, token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
)
async def get_profile(token: str = Depends(require_bearer_token)) -> UserResponse:
    # TODO: extract user_id from token claims
    user_id: UUID = ...  # type: ignore[assignment]
    return await _svc.get_profile(user_id)


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the authenticated user's password",
)
async def change_password(
    payload: ChangePasswordRequest,
    token: str = Depends(require_bearer_token),
) -> None:
    # TODO: extract user_id from token claims
    user_id: UUID = ...  # type: ignore[assignment]
    await _svc.change_password(user_id, payload.current_password, payload.new_password)
