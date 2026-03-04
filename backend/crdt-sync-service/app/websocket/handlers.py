"""
app/websocket/handlers.py — CRDT Sync Service
───────────────────────────────────────────────
Message-type dispatch for incoming WebSocket frames.
Each handler receives the parsed message and connection context.

Message flow:
  Client → handle_message() → route by type → handler → broadcast / unicast
"""

import logging
from uuid import UUID

from app.models.schemas import SyncOperationRequest
from app.websocket.manager import ConnectionManager

logger = logging.getLogger("crdt-sync.handlers")


async def handle_message(
    raw: dict,
    room_id: UUID,
    user_id: UUID,
    connection_id: str,
    manager: ConnectionManager,
) -> None:
    """
    Entry point for all incoming WebSocket messages.
    Dispatches to the appropriate handler based on `raw["type"]`.

    TODO:
      1. Parse `raw["type"]` (use MessageType enum from shared/models.py)
      2. Dispatch to the correct handler below
      3. Catch validation errors and send back an error frame
    """
    raise NotImplementedError


async def handle_operation(
    payload: dict,
    room_id: UUID,
    user_id: UUID,
    connection_id: str,
    manager: ConnectionManager,
) -> None:
    """
    Process a CRDT operation from a client and broadcast to the room.

    TODO:
      1. Validate payload against SyncOperationRequest schema
      2. Apply server-side logical clock (max(server, client) + 1)
      3. Validate the op is semantically valid for the current room state
      4. Broadcast SyncOperationBroadcast to all other connections
      5. Async-fire to Persistence Service (don't block the broadcast)
    """
    raise NotImplementedError


async def handle_sync_request(
    payload: dict,
    room_id: UUID,
    user_id: UUID,
    connection_id: str,
    manager: ConnectionManager,
) -> None:
    """
    A newly connected client requests the current board state.

    TODO:
      1. Fetch latest snapshot from Persistence Service
      2. Build SyncStateResponse (snapshot + lamport_clock + connected_users)
      3. Unicast only to the requesting connection_id
    """
    raise NotImplementedError


async def handle_presence_update(
    payload: dict,
    room_id: UUID,
    user_id: UUID,
    connection_id: str,
    manager: ConnectionManager,
) -> None:
    """
    Relay an ephemeral cursor / presence update to the room.
    Do NOT persist these — they are purely real-time.

    TODO:
      1. Validate payload against PresenceUpdate schema
      2. Broadcast to all other connections in the room
    """
    raise NotImplementedError
