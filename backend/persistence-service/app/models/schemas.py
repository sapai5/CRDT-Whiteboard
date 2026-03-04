"""app/models/schemas.py — Persistence Service request/response schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


# ── Requests ──────────────────────────────────────────────────────────────────

class SaveSnapshotRequest(BaseModel):
    """Posted by CRDT Sync Service to persist the current board state."""
    lamport_clock: int
    snapshot: dict[str, Any]


class SaveOperationRequest(BaseModel):
    """Individual CRDT op written to the operation log for replay/audit."""
    op_id: UUID
    user_id: UUID
    op_type: str
    lamport_clock: int
    payload: dict[str, Any]


# ── Responses ─────────────────────────────────────────────────────────────────

class SnapshotResponse(BaseModel):
    room_id: UUID
    lamport_clock: int
    snapshot: dict[str, Any]
    saved_at: datetime


class BoardMetaResponse(BaseModel):
    """Lightweight metadata about a stored board (no snapshot payload)."""
    room_id: UUID
    lamport_clock: int
    operation_count: int
    last_modified_at: datetime
    created_at: datetime


class OperationLogEntry(BaseModel):
    op_id: UUID
    room_id: UUID
    user_id: UUID
    op_type: str
    lamport_clock: int
    payload: dict[str, Any]
    recorded_at: datetime
