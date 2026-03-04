"""app/models/schemas.py — CRDT Sync Service schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SyncOperationRequest(BaseModel):
    """Sent by the client over WebSocket to broadcast a CRDT op."""
    op_id: UUID
    op_type: str  # matches OperationType enum in shared/models.py
    lamport_clock: int
    payload: dict[str, Any]


class SyncOperationBroadcast(BaseModel):
    """Forwarded to all other clients in the room after server-side validation."""
    op_id: UUID
    room_id: UUID
    user_id: UUID
    op_type: str
    lamport_clock: int
    payload: dict[str, Any]
    server_timestamp: datetime = Field(default_factory=datetime.utcnow)


class PresenceUpdate(BaseModel):
    """Ephemeral cursor / presence payload. Never persisted."""
    user_id: UUID
    display_name: str
    cursor_x: float | None = None
    cursor_y: float | None = None
    color: str = "#000000"


class SyncStateResponse(BaseModel):
    """
    Full board state sent to a newly connected client (catch-up sync).
    The `snapshot` is the serialized CRDT document from Persistence Service.
    """
    room_id: UUID
    snapshot: dict[str, Any]
    lamport_clock: int
    connected_users: list[PresenceUpdate] = []


class ConnectionInfo(BaseModel):
    """Metadata about an active WebSocket connection."""
    connection_id: str
    room_id: UUID
    user_id: UUID
    connected_at: datetime
