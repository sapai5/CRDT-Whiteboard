"""
app/routes/boards.py — Persistence Service
────────────────────────────────────────────
REST endpoints for snapshot storage and operation log.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.schemas import (
    BoardMetaResponse,
    OperationLogEntry,
    SaveOperationRequest,
    SaveSnapshotRequest,
    SnapshotResponse,
)
from app.services.persistence_service import PersistenceService

router = APIRouter(prefix="/boards", tags=["Boards"])
_svc = PersistenceService()


# ── Snapshots ──────────────────────────────────────────────────────────────────

@router.get(
    "/{room_id}/snapshot",
    response_model=SnapshotResponse,
    summary="Fetch the latest board snapshot",
)
async def get_snapshot(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> SnapshotResponse:
    return await _svc.get_snapshot(room_id)


@router.post(
    "/{room_id}/snapshot",
    response_model=SnapshotResponse,
    summary="[Internal] Save / overwrite the board snapshot (called by CRDT Sync)",
)
async def save_snapshot(
    room_id: UUID,
    payload: SaveSnapshotRequest,
    user: CurrentUser = Depends(get_current_user),
) -> SnapshotResponse:
    return await _svc.save_snapshot(room_id, payload)


@router.delete(
    "/{room_id}/snapshot",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard-delete a board snapshot",
)
async def delete_snapshot(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> None:
    await _svc.delete_snapshot(room_id)


# ── Operation log ──────────────────────────────────────────────────────────────

@router.post(
    "/{room_id}/operations",
    response_model=OperationLogEntry,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Append an operation to the log (called by CRDT Sync)",
)
async def append_operation(
    room_id: UUID,
    payload: SaveOperationRequest,
    user: CurrentUser = Depends(get_current_user),
) -> OperationLogEntry:
    return await _svc.append_operation(room_id, payload)


@router.get(
    "/{room_id}/operations",
    response_model=list[OperationLogEntry],
    summary="Fetch operations since a given Lamport clock value",
)
async def get_operations(
    room_id: UUID,
    since_lamport: int = 0,
    limit: int = 1000,
    user: CurrentUser = Depends(get_current_user),
) -> list[OperationLogEntry]:
    return await _svc.get_operations(room_id, since_lamport, limit)


# ── Board metadata ─────────────────────────────────────────────────────────────

@router.get(
    "/{room_id}",
    response_model=BoardMetaResponse,
    summary="Get board metadata (no snapshot payload)",
)
async def get_board_meta(
    room_id: UUID,
    user: CurrentUser = Depends(get_current_user),
) -> BoardMetaResponse:
    return await _svc.get_board_meta(room_id)
