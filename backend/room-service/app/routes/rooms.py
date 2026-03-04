"""
app/routes/rooms.py — Room Service
────────────────────────────────────
REST endpoints for room and participant management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.schemas import (
    CreateRoomRequest,
    InviteParticipantRequest,
    JoinRoomResponse,
    ParticipantResponse,
    RoomDetailResponse,
    RoomResponse,
    UpdateRoomRequest,
)
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])
_svc = RoomService()


# ── Room CRUD ──────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new whiteboard room",
)
async def create_room(
    payload: CreateRoomRequest,
    user: CurrentUser = Depends(get_current_user),
) -> RoomResponse:
    return await _svc.create_room(payload, user.user_id)


@router.get(
    "/",
    response_model=list[RoomResponse],
    summary="List rooms the authenticated user belongs to",
)
async def list_rooms(
    user: CurrentUser = Depends(get_current_user),
) -> list[RoomResponse]:
    return await _svc.list_rooms(user.user_id)


@router.get(
    "/{room_id}",
    response_model=RoomDetailResponse,
    summary="Get room details and participant list",
)
async def get_room(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> RoomDetailResponse:
    return await _svc.get_room(room_id)


@router.patch(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Update room metadata (owner only)",
)
async def update_room(
    room_id: UUID,
    payload: UpdateRoomRequest,
    user: CurrentUser = Depends(get_current_user),
) -> RoomResponse:
    return await _svc.update_room(room_id, payload, user.user_id)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive (soft-delete) a room (owner only)",
)
async def archive_room(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> None:
    await _svc.archive_room(room_id, user.user_id)


# ── Join / Leave ───────────────────────────────────────────────────────────────

@router.post(
    "/{room_id}/join",
    response_model=JoinRoomResponse,
    summary="Join a room and receive a WebSocket ticket",
)
async def join_room(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> JoinRoomResponse:
    return await _svc.join_room(room_id, user.user_id)


@router.post(
    "/{room_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Leave a room",
)
async def leave_room(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> None:
    await _svc.leave_room(room_id, user.user_id)


# ── Participants ───────────────────────────────────────────────────────────────

@router.get(
    "/{room_id}/participants",
    response_model=list[ParticipantResponse],
    summary="List current participants and their online status",
)
async def list_participants(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> list[ParticipantResponse]:
    return await _svc.list_participants(room_id)


@router.post(
    "/{room_id}/participants",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to the room",
)
async def invite_participant(
    room_id: UUID,
    payload: InviteParticipantRequest,
    user: CurrentUser = Depends(get_current_user),
) -> ParticipantResponse:
    return await _svc.invite_participant(room_id, payload, user.user_id)


@router.patch(
    "/{room_id}/participants/{target_user_id}",
    response_model=ParticipantResponse,
    summary="Change a participant's role (owner only)",
)
async def update_participant_role(
    room_id: UUID,
    target_user_id: UUID,
    new_role: str,
    user: CurrentUser = Depends(get_current_user),
) -> ParticipantResponse:
    return await _svc.update_participant_role(room_id, target_user_id, new_role, user.user_id)
