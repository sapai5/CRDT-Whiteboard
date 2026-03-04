"""
app/websocket/manager.py — CRDT Sync Service
──────────────────────────────────────────────
Manages active WebSocket connections per room.
Provides broadcast and unicast helpers.

TODO: For multi-instance deployments, replace the in-memory registry
      with a pub/sub backend (e.g. Redis Pub/Sub) so that ops broadcast
      across multiple CRDT service replicas.
"""

import logging
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger("crdt-sync.manager")


class ConnectionManager:
    """
    In-memory registry: room_id → {connection_id: WebSocket}.

    Thread-safety note: FastAPI runs handlers in a single asyncio event loop,
    so dict mutations are safe without locks in a single-process setup.
    """

    def __init__(self) -> None:
        # room_id (str) → { connection_id (str) → WebSocket }
        self._rooms: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        # connection_id → (room_id, user_id) for reverse lookup
        self._meta: dict[str, tuple[str, str]] = {}

    # ── Connection lifecycle ──────────────────────────────────────────────────

    async def connect(
        self, websocket: WebSocket, room_id: UUID, user_id: UUID, connection_id: str
    ) -> None:
        """
        Accept and register a new WebSocket connection.

        TODO:
          1. Call websocket.accept()
          2. Enforce max_connections_per_room limit
          3. Store connection in self._rooms and self._meta
          4. Log join event
        """
        raise NotImplementedError

    async def disconnect(self, connection_id: str) -> None:
        """
        Remove a connection from the registry on close/error.

        TODO:
          1. Look up room_id via self._meta
          2. Remove from self._rooms[room_id]
          3. Clean up self._meta entry
          4. If room becomes empty, optionally trigger a snapshot flush
        """
        raise NotImplementedError

    # ── Messaging ─────────────────────────────────────────────────────────────

    async def broadcast(
        self, room_id: UUID, message: str, exclude_connection_id: str | None = None
    ) -> None:
        """
        Send a JSON string to all connections in a room, optionally excluding
        the sender (so they don't echo their own op).

        TODO:
          1. Iterate self._rooms[str(room_id)]
          2. Skip exclude_connection_id if provided
          3. Call websocket.send_text(message) for each
          4. Handle stale/closed connections gracefully (remove on error)
        """
        raise NotImplementedError

    async def send_to(self, connection_id: str, message: str) -> None:
        """
        Send a JSON string to a single connection (e.g. for catch-up sync).

        TODO:
          1. Resolve WebSocket from self._meta + self._rooms
          2. Call websocket.send_text(message)
        """
        raise NotImplementedError

    # ── Introspection ─────────────────────────────────────────────────────────

    def room_connection_count(self, room_id: UUID) -> int:
        """Return the number of active connections in a room."""
        return len(self._rooms.get(str(room_id), {}))

    def active_rooms(self) -> list[str]:
        """Return room IDs that have at least one active connection."""
        return [rid for rid, conns in self._rooms.items() if conns]


# Singleton used across the service
manager = ConnectionManager()
