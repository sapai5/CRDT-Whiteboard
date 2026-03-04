"""
app/services/sync_service.py — CRDT Sync Service
──────────────────────────────────────────────────
Orchestrates authentication of WS connections, snapshot flushing,
and inter-service calls (Persistence, Room).
"""

import logging
from uuid import UUID

import httpx

from app.config import settings

logger = logging.getLogger("crdt-sync.service")


class SyncService:

    async def validate_ws_ticket(self, ticket: str) -> tuple[UUID, UUID]:
        """
        Verify the short-lived WS ticket issued by Room Service on join.
        Returns (user_id, room_id) on success.

        TODO:
          1. Decode the signed ticket (same JWT secret or a dedicated one)
          2. Check expiry (tickets should be very short-lived, ~60s)
          3. Return (user_id, room_id)
          4. Raise AuthenticationError on failure
        """
        raise NotImplementedError

    async def flush_snapshot(self, room_id: UUID, snapshot: dict) -> None:
        """
        Push the current in-memory CRDT state to the Persistence Service.
        Called periodically and on room-empty events.

        TODO:
          1. Serialize snapshot to JSON
          2. POST to persistence-service /boards/{room_id}/snapshot
          3. Handle failures gracefully (retry or log and skip)
        """
        raise NotImplementedError

    async def fetch_snapshot(self, room_id: UUID) -> dict:
        """
        Pull the latest board snapshot from the Persistence Service.
        Called when serving a sync_request to a newly connected client.

        TODO:
          1. GET persistence-service /boards/{room_id}/snapshot
          2. Return the snapshot dict (empty dict for brand-new rooms)
        """
        raise NotImplementedError

    async def notify_room_empty(self, room_id: UUID) -> None:
        """
        Called when the last connection in a room disconnects.
        Triggers a final snapshot flush and optionally notifies Room Service.

        TODO:
          1. Call self.flush_snapshot with latest state
          2. Optionally PATCH room-service /rooms/{room_id} with last_active_at
        """
        raise NotImplementedError
