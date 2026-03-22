"""
app/services/auth_service.py — Auth Service
────────────────────────────────────────────
Authentication logic: registration, login, token management, and profile.
"""

from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import RefreshTokenRecord, UserRecord
from app.models.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UpdateProfileRequest,
    UserResponse,
    ValidateTokenResponse,
)
from app.services.token_utils import (
    blocklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_blocklisted,
    verify_password,
)
from jose import JWTError
import hashlib

def _hash_token(token: str) -> str:
    """SHA-256 hash of a token string for safe DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:

    # ── Registration ──────────────────────────────────────────────────────────

    async def register(self, payload: RegisterRequest, db: Session) -> UserResponse:
        """
        Create a new user account.

          1. Check email uniqueness
          2. Hash password with bcrypt
          3. Persist user record
          4. Return UserResponse (never return raw password)
        """
        # 1. Check email uniqueness
        existing = db.query(UserRecord).filter(UserRecord.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )

        # 2. Hash password with bcrypt
        hashed_pw = hash_password(payload.password)

        # 3. Persist user record
        user = UserRecord(
            email=payload.email,
            display_name=payload.display_name,
            password_hash=hashed_pw,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )

        # 4. Return UserResponse (never return raw password)
        return UserResponse(
            user_id=UUID(user.user_id),
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )

    # ── Login / Logout ────────────────────────────────────────────────────────

    async def login(self, payload: LoginRequest, db: Session) -> TokenPair:
        """
        Authenticate a user and issue a JWT access + refresh token pair.

          1. Fetch user by email
          2. Verify password hash
          3. Issue access token (short-lived)
          4. Issue refresh token (long-lived, store hash in DB)
        """
        # 1. Fetch user by email
        user = db.query(UserRecord).filter(UserRecord.email == payload.email).first()

        # 2. Verify password hash — use constant-time check to resist timing attacks.
        #    Deliberately avoid revealing *why* login failed (no "user not found" vs "wrong password").
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled.",
            )

        # 3. Issue access token (short-lived)
        access_tok, expires_in = create_access_token(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
        )

        # 4. Issue refresh token (long-lived) and store its hash in DB
        refresh_tok, refresh_exp = create_refresh_token(user_id=user.user_id)
        db.add(RefreshTokenRecord(
            user_id=user.user_id,
            token_hash=_hash_token(refresh_tok),
            expires_at=refresh_exp,
        ))
        db.commit()

        return TokenPair(
            access_token=access_tok,
            refresh_token=refresh_tok,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def logout(self, user_id: UUID, access_token: str, db: Session) -> None:
        """
        Invalidate the current session.

          1. Blocklist the access token JTI (in-memory; swap for Redis in prod)
          2. Revoke all refresh tokens for this user
        """
        # 1. Blocklist the access token so it can't be reused before it expires
        try:
            payload = decode_token(access_token)
            jti = payload.get("jti")
            if jti:
                blocklist_token(jti)
        except JWTError:
            pass  # Already expired tokens are effectively invalid — safe to ignore

        # 2. Revoke all refresh tokens for this user so they can't re-issue
        db.query(RefreshTokenRecord).filter(
            RefreshTokenRecord.user_id == str(user_id)
        ).update({"revoked": True})
        db.commit()

    # ── Token lifecycle ───────────────────────────────────────────────────────

    async def refresh(self, payload: RefreshRequest, db: Session) -> TokenPair:
        """
        Exchange a valid refresh token for a new token pair (rotation).

          1. Decode and verify refresh token signature
          2. Look up the token hash in DB — reject if revoked or not found
          3. Issue new pair and invalidate old refresh token (rotation)
        """
        # 1. Decode and verify refresh token signature
        try:
            claims = decode_token(payload.refresh_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Reject if the token type isn't the expected refresh type
        if claims.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not a refresh token.",
            )

        user_id = claims.get("sub")

        # 2. Look up the hashed token in DB — guard against replay after rotation
        token_hash = _hash_token(payload.refresh_token)
        record = db.query(RefreshTokenRecord).filter(
            RefreshTokenRecord.user_id == user_id,
            RefreshTokenRecord.token_hash == token_hash,
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not recognised.",
            )

        if record.revoked:
            # Token already used — possible replay attack; revoke ALL tokens for this user
            db.query(RefreshTokenRecord).filter(
                RefreshTokenRecord.user_id == user_id
            ).update({"revoked": True})
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token already used. All sessions revoked.",
            )

        # Fetch user to embed fresh claims in the new tokens
        user = db.query(UserRecord).filter(UserRecord.user_id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account not found or disabled.",
            )

        # 3. Invalidate old refresh token (mark as rotated)
        record.revoked = True

        # Issue new pair
        access_tok, expires_in = create_access_token(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
        )
        refresh_tok, refresh_exp = create_refresh_token(user_id=user.user_id)
        db.add(RefreshTokenRecord(
            user_id=user.user_id,
            token_hash=_hash_token(refresh_tok),
            expires_at=refresh_exp,
        ))
        db.commit()

        return TokenPair(
            access_token=access_tok,
            refresh_token=refresh_tok,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def validate_token(self, token: str) -> ValidateTokenResponse:
        """
        Verify an access token and return the embedded claims.
        Called by other services via internal REST to authenticate requests.
        Always returns ValidateTokenResponse — never raises, so callers can
        branch on the `valid` field.

          1. Decode JWT with secret (catches expiry and bad signature)
          2. Check token type is 'access'
          3. Check JTI against blocklist
          4. Return claims on success, valid=False on any failure
        """
        try:
            # 1. Decode — jose raises JWTError if expired or signature invalid
            claims = decode_token(token)

            # 2. Must be an access token, not a refresh token
            if claims.get("type") != "access":
                return ValidateTokenResponse(valid=False)

            # 3. Reject if this JTI was blocklisted on logout
            jti = claims.get("jti")
            if jti and is_blocklisted(jti):
                return ValidateTokenResponse(valid=False)

            # 4. All good — return the embedded user claims
            return ValidateTokenResponse(
                valid=True,
                user_id=UUID(claims["sub"]),
                email=claims.get("email"),
                display_name=claims.get("display_name"),
            )

        except (JWTError, KeyError, ValueError):
            return ValidateTokenResponse(valid=False)

    # ── Profile ───────────────────────────────────────────────────────────────

    async def get_profile(self, user_id: UUID, db: Session) -> UserResponse:
        """Fetch the public profile of a user by ID."""
        user = db.query(UserRecord).filter(UserRecord.user_id == str(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return UserResponse(
            user_id=UUID(user.user_id),
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )

    async def update_profile(
        self, user_id: UUID, payload: UpdateProfileRequest, db: Session
    ) -> UserResponse:
        """Update the user's profile information (e.g. username/display_name)."""
        user = db.query(UserRecord).filter(UserRecord.user_id == str(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if payload.display_name is not None:
            user.display_name = payload.display_name
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url

        db.commit()
        db.refresh(user)

        return UserResponse(
            user_id=UUID(user.user_id),
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str, db: Session
    ) -> None:
        """Verify current password and replace with new hash, revoking old sessions."""
        user = db.query(UserRecord).filter(UserRecord.user_id == str(user_id)).first()
        if not user or not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password.",
            )

        # Hash new password
        user.password_hash = hash_password(new_password)

        # Force a logout on all other devices by revoking existing refresh tokens
        db.query(RefreshTokenRecord).filter(
            RefreshTokenRecord.user_id == str(user_id)
        ).update({"revoked": True})

        db.commit()
