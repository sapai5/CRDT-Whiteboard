"""
app/services/auth_service.py — Auth Service
────────────────────────────────────────────
All methods are stubs. Implement each one:
  - Hash passwords with passlib/bcrypt
  - Issue / verify JWTs with python-jose
  - Persist users to a database (e.g. SQLite → Postgres)
"""

from uuid import UUID

from app.models.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserResponse,
    ValidateTokenResponse,
)


class AuthService:

    # ── Registration ──────────────────────────────────────────────────────────

    async def register(self, payload: RegisterRequest) -> UserResponse:
        """
        Create a new user account.

        TODO:
          1. Check email uniqueness
          2. Hash password with bcrypt
          3. Persist user record
          4. Return UserResponse (never return raw password)
        """
        raise NotImplementedError

    # ── Login / Logout ────────────────────────────────────────────────────────

    async def login(self, payload: LoginRequest) -> TokenPair:
        """
        Authenticate a user and issue a JWT access + refresh token pair.

        TODO:
          1. Fetch user by email
          2. Verify password hash
          3. Issue access token (short-lived)
          4. Issue refresh token (long-lived, store hash in DB)
        """
        raise NotImplementedError

    async def logout(self, user_id: UUID, access_token: str) -> None:
        """
        Invalidate the current session.

        TODO:
          1. Blocklist the access token (Redis TTL or DB flag)
          2. Delete / expire the refresh token record
        """
        raise NotImplementedError

    # ── Token lifecycle ───────────────────────────────────────────────────────

    async def refresh(self, payload: RefreshRequest) -> TokenPair:
        """
        Exchange a valid refresh token for a new token pair (rotation).

        TODO:
          1. Decode and verify refresh token signature
          2. Check token is not already rotated / revoked
          3. Issue new pair and invalidate old refresh token
        """
        raise NotImplementedError

    async def validate_token(self, token: str) -> ValidateTokenResponse:
        """
        Verify an access token and return the embedded claims.
        Called by other services via internal REST to authenticate requests.

        TODO:
          1. Decode JWT with secret
          2. Check expiry, blocklist
          3. Return ValidateTokenResponse with user claims
        """
        raise NotImplementedError

    # ── Profile ───────────────────────────────────────────────────────────────

    async def get_profile(self, user_id: UUID) -> UserResponse:
        """
        Fetch the public profile of a user by ID.

        TODO: Query user record from DB
        """
        raise NotImplementedError

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        """
        Verify current password then replace with new hash.

        TODO:
          1. Fetch + verify current hash
          2. Hash new password
          3. Persist and revoke all existing refresh tokens
        """
        raise NotImplementedError
