"""
app/services/persistence_service.py — Persistence Service
──────────────────────────────────────────────────────────
All methods are stubs. Implement storage with aiosqlite (dev)
or swap DATABASE_URL to Postgres + asyncpg for production.
"""

from uuid import UUID

from app.models.schemas import (
    BoardMetaResponse,
    OperationLogEntry,
    SaveOperationRequest,
    SaveSnapshotRequest,
    SnapshotResponse,
)


class PersistenceService:

    # ── Snapshots ─────────────────────────────────────────────────────────────

    async def save_snapshot(
        self, room_id: UUID, payload: SaveSnapshotRequest
    ) -> SnapshotResponse:
        """
        Upsert the latest board snapshot for a room.

        TODO:
          1. Serialize payload.snapshot to JSON
          2. UPSERT into `board_snapshots` table (room_id PK or unique key)
          3. Return SnapshotResponse with saved_at timestamp
        """
        raise NotImplementedError

    async def get_snapshot(self, room_id: UUID) -> SnapshotResponse:
        """
        Retrieve the latest board snapshot.

        TODO:
          1. SELECT from `board_snapshots` WHERE room_id = ?
          2. Raise BoardNotFoundError if no row exists
          3. Deserialize JSON snapshot and return SnapshotResponse
        """
        raise NotImplementedError

    async def delete_snapshot(self, room_id: UUID) -> None:
        """
        Hard-delete a board snapshot (e.g. on room deletion).

        TODO: DELETE FROM board_snapshots WHERE room_id = ?
        """
        raise NotImplementedError

    # ── Operation log ─────────────────────────────────────────────────────────

    async def append_operation(
        self, room_id: UUID, payload: SaveOperationRequest
    ) -> OperationLogEntry:
        """
        Append a single CRDT op to the immutable operation log.
        Enables full replay and audit trails.

        TODO:
          1. INSERT into `operation_log` (op_id, room_id, user_id, ...)
          2. Return OperationLogEntry with recorded_at
        """
        raise NotImplementedError

    async def get_operations(
        self,
        room_id: UUID,
        since_lamport: int = 0,
        limit: int = 1000,
    ) -> list[OperationLogEntry]:
        """
        Fetch operations for a room since a given logical clock value.
        Used for partial catch-up (e.g. short disconnection).

        TODO:
          1. SELECT from `operation_log` WHERE room_id=? AND lamport_clock > ?
          2. ORDER BY lamport_clock ASC LIMIT ?
        """
        raise NotImplementedError

    # ── Board metadata ────────────────────────────────────────────────────────

    async def get_board_meta(self, room_id: UUID) -> BoardMetaResponse:
        """
        Return lightweight metadata about a board without the full snapshot.

        TODO:
          1. JOIN snapshot + COUNT(operation_log) WHERE room_id = ?
        """
        raise NotImplementedError

    async def list_boards(self, room_ids: list[UUID]) -> list[BoardMetaResponse]:
        """
        Batch-fetch metadata for multiple rooms (called by Room Service).

        TODO: SELECT ... WHERE room_id IN (?)
        """
        raise NotImplementedError
