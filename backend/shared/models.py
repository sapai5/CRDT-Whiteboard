"""
shared/models.py
────────────────
Common Pydantic schemas and enums shared across all microservices.
Import these instead of duplicating type definitions per service.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class RoomStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class OperationType(str, Enum):
    """High-level CRDT operation categories broadcast over WebSocket."""
    INSERT = "insert"
    DELETE = "delete"
    MOVE = "move"
    STYLE = "style"
    CURSOR = "cursor"      # ephemeral — not persisted
    PRESENCE = "presence"  # ephemeral — not persisted


class MessageType(str, Enum):
    """WebSocket message envelope types."""
    OPERATION = "operation"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    PRESENCE_UPDATE = "presence_update"
    ERROR = "error"
    ACK = "ack"


# ── Common response envelopes ─────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: str | None = None


# ── Shared entity stubs ───────────────────────────────────────────────────────

class UserSummary(BaseModel):
    """Lightweight user reference embedded in other payloads."""
    user_id: UUID
    display_name: str
    avatar_url: str | None = None


class RoomSummary(BaseModel):
    """Lightweight room reference embedded in other payloads."""
    room_id: UUID
    name: str
    status: RoomStatus


class CRDTOperation(BaseModel):
    """
    A single CRDT operation. The `payload` is intentionally opaque here;
    each service validates it against its own stricter schema.
    """
    op_id: UUID
    room_id: UUID
    user_id: UUID
    op_type: OperationType
    lamport_clock: int = Field(..., description="Logical clock for ordering")
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WebSocketMessage(BaseModel):
    """Envelope for every message sent/received over the WebSocket channel."""
    type: MessageType
    room_id: UUID
    sender_id: UUID
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
