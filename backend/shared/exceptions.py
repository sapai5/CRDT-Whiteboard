"""
shared/exceptions.py
─────────────────────
Domain exceptions shared across all microservices.
Each service catches these and maps them to HTTP / WS error codes.
"""


class WhiteboardBaseError(Exception):
    """Root exception for all whiteboard domain errors."""


# ── Auth ──────────────────────────────────────────────────────────────────────

class AuthenticationError(WhiteboardBaseError):
    """Raised when credentials are missing or invalid."""


class AuthorizationError(WhiteboardBaseError):
    """Raised when an authenticated user lacks permission."""


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT has expired."""


# ── Room ──────────────────────────────────────────────────────────────────────

class RoomNotFoundError(WhiteboardBaseError):
    """Raised when a requested room does not exist."""


class RoomFullError(WhiteboardBaseError):
    """Raised when a room has reached its maximum connection limit."""


class RoomArchivedError(WhiteboardBaseError):
    """Raised when attempting to write to an archived room."""


# ── CRDT Sync ─────────────────────────────────────────────────────────────────

class InvalidOperationError(WhiteboardBaseError):
    """Raised when a CRDT operation payload fails validation."""


class SyncConflictError(WhiteboardBaseError):
    """Raised when a sync conflict cannot be resolved automatically."""


# ── Persistence ───────────────────────────────────────────────────────────────

class BoardNotFoundError(WhiteboardBaseError):
    """Raised when a saved board snapshot cannot be found."""


class PersistenceError(WhiteboardBaseError):
    """Raised on unrecoverable storage failures."""
