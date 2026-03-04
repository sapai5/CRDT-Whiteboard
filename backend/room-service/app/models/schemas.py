"""app/models/schemas.py — Room Service request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────────────────────

class CreateRoomRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = Field(None, max_length=512)
    max_participants: int = Field(default=50, ge=2, le=500)


class UpdateRoomRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    max_participants: int | None = Field(None, ge=2, le=500)


class InviteParticipantRequest(BaseModel):
    user_id: UUID
    role: str = Field(default="editor", pattern="^(editor|viewer)$")


# ── Responses ─────────────────────────────────────────────────────────────────

class ParticipantResponse(BaseModel):
    user_id: UUID
    display_name: str
    role: str
    joined_at: datetime
    is_online: bool = False


class RoomResponse(BaseModel):
    room_id: UUID
    name: str
    description: str | None
    owner_id: UUID
    max_participants: int
    participant_count: int
    status: str
    created_at: datetime
    updated_at: datetime


class RoomDetailResponse(RoomResponse):
    participants: list[ParticipantResponse] = []


class JoinRoomResponse(BaseModel):
    room_id: UUID
    ws_ticket: str  # short-lived token the CRDT service validates for WS upgrade
    role: str
