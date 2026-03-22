#handling anything JWT related
"""
app/services/token_utils.py — Auth Service
────────────────────────────────────────────
JWT creation, verification, and access token blocklist.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

#Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the bcrypt hash."""
    return pwd_context.verify(plain, hashed)

#Token creation
def create_access_token(user_id: str, email: str, display_name: str) -> tuple[str, int]:
    """
    Issue a short-lived JWT access token.
    Returns (token, expires_in_seconds).
    """
    expires_in = settings.access_token_expire_minutes * 60
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "display_name": display_name,
        "type": "access",
        "jti": str(uuid4()),  # unique token ID for blocklisting
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_in

def create_refresh_token(user_id: str) -> tuple[str, datetime]:
    """
    Issue a long-lived JWT refresh token.
    Returns (token, expires_at datetime).
    """
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": str(uuid4()),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at

#Token verification
def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT. Raises JWTError if invalid or expired.
    Returns the payload dict.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

#Access token blocklist
_blocklist: set[str] = set()
def blocklist_token(jti: str) -> None:
    """Add a token's JTI to the blocklist on logout."""
    _blocklist.add(jti)

def is_blocklisted(jti: str) -> bool:
    """Return True if the token has been blocklisted."""
    return jti in _blocklist