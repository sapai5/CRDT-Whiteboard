"""
crdt-sync-service/main.py — CRDT Sync Service entrypoint
──────────────────────────────────────────────────────────
Exposes:
  WS  /ws/{room_id}?ticket=<ws_ticket>   — real-time CRDT sync
  GET /rooms/{room_id}/connections        — active connection count (internal)
"""

import logging
from uuid import UUID

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.sync_service import SyncService
from app.websocket.handlers import handle_message
from app.websocket.manager import manager

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger("crdt-sync")

app = FastAPI(
    title="Whiteboard — CRDT Sync Service",
    description="WebSocket hub for real-time CRDT operation broadcast.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_sync_svc = SyncService()


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: UUID,
    ticket: str = Query(..., description="Short-lived WS ticket from Room Service"),
) -> None:
    """
    Main WebSocket endpoint. Connection lifecycle:
      1. Validate WS ticket → extract user_id
      2. Register connection with ConnectionManager
      3. Send initial sync_request response (current board state)
      4. Enter receive loop — dispatch messages to handlers
      5. On disconnect, clean up and optionally flush snapshot

    TODO: Implement each step in handlers.py and sync_service.py
    """
    connection_id: str | None = None
    try:
        # Step 1 — validate ticket
        user_id, validated_room_id = await _sync_svc.validate_ws_ticket(ticket)

        # Step 2 — register connection
        import uuid
        connection_id = str(uuid.uuid4())
        await manager.connect(websocket, room_id, user_id, connection_id)

        # Step 3 — send initial state
        # TODO: call handle_sync_request here

        # Step 4 — receive loop
        while True:
            raw = await websocket.receive_json()
            await handle_message(raw, room_id, user_id, connection_id, manager)

    except WebSocketDisconnect:
        logger.info("Client disconnected: %s", connection_id)
    except Exception as exc:
        logger.exception("Unhandled WS error: %s", exc)
    finally:
        if connection_id:
            await manager.disconnect(connection_id)
            if manager.room_connection_count(room_id) == 0:
                await _sync_svc.notify_room_empty(room_id)


# ── REST endpoints (internal) ─────────────────────────────────────────────────

@app.get("/rooms/{room_id}/connections", tags=["Internal"])
async def get_connection_count(room_id: UUID) -> dict:
    """Return the number of active WebSocket connections in a room."""
    return {
        "room_id": str(room_id),
        "connection_count": manager.room_connection_count(room_id),
    }


@app.get("/rooms/active", tags=["Internal"])
async def get_active_rooms() -> dict:
    """Return all room IDs that currently have active connections."""
    return {"active_rooms": manager.active_rooms()}


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"service": "crdt-sync", "status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.service_port, reload=True)
