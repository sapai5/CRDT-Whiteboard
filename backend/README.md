# Whiteboard Backend — Microservice Architecture

Real-time collaborative whiteboard backend built with **FastAPI** + **WebSockets**.
CRDT conflict resolution keeps every client's canvas eventually consistent.

---

## Services

| Service | Port | Responsibility |
|---|---|---|
| **auth-service** | `8001` | JWT issue/validation, user accounts |
| **room-service** | `8002` | Room CRUD, participants, WS tickets |
| **crdt-sync-service** | `8003` | WebSocket hub, op broadcast, presence |
| **persistence-service** | `8004` | Snapshot storage, operation log |

---

## Quick Start

```bash
cp .env.example .env          # fill in secrets
docker compose up --build
```

Swagger UI per service:
- Auth:        http://localhost:8001/docs
- Room:        http://localhost:8002/docs
- CRDT Sync:   http://localhost:8003/docs
- Persistence: http://localhost:8004/docs

---

## Request Flow

### REST (auth + room management)
```
Client → auth-service  POST /auth/login          → TokenPair
Client → room-service  POST /rooms               → RoomResponse
Client → room-service  POST /rooms/{id}/join     → JoinRoomResponse (+ ws_ticket)
```

### WebSocket (real-time CRDT sync)
```
Client → crdt-sync-service  WS /ws/{room_id}?ticket=<ws_ticket>
  ↓ on connect  → sync_request  → fetch snapshot from persistence-service
  ↓ op received → validate → broadcast to room → async log to persistence-service
  ↓ on cursor   → presence_update → broadcast (not persisted)
  ↓ on close    → flush snapshot if room empty
```

---

## WebSocket Message Schema

All frames follow this envelope:

```json
{
  "type": "operation | sync_request | sync_response | presence_update | error | ack",
  "room_id": "<uuid>",
  "sender_id": "<uuid>",
  "payload": { ... },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## Implementation TODOs

Every service method is a stub with a `raise NotImplementedError` and a `TODO` comment
describing exactly what to implement. Start here:

1. **auth-service** `app/services/auth_service.py`
   - `register` → hash password (bcrypt), persist user
   - `login` → verify hash, issue JWT pair
   - `validate_token` → decode + verify JWT (used by all other services)

2. **room-service** `app/services/room_service.py`
   - `create_room`, `join_room` (issues WS ticket), `list_participants`

3. **crdt-sync-service**
   - `app/websocket/manager.py` → `connect`, `disconnect`, `broadcast`
   - `app/websocket/handlers.py` → `handle_operation`, `handle_sync_request`
   - `app/services/sync_service.py` → `validate_ws_ticket`, `flush_snapshot`

4. **persistence-service** `app/services/persistence_service.py`
   - `save_snapshot`, `get_snapshot`, `append_operation`
   - Add DB init / migration (Alembic recommended for Postgres)

---

## Shared Code

`shared/` contains Pydantic models and exceptions imported by all services.
In a monorepo, install it as a local package. In Docker, copy it into each
service image (or use a private PyPI / build layer).

---

## Production Checklist

- [ ] Replace SQLite with Postgres (`DATABASE_URL`)
- [ ] Replace in-memory WS registry with Redis Pub/Sub (multi-replica CRDT sync)
- [ ] Lock down CORS origins
- [ ] Add rate limiting (e.g. `slowapi`)
- [ ] Add structured logging (e.g. `structlog`)
- [ ] Set up Alembic migrations
- [ ] Add an API Gateway / reverse proxy (nginx or Traefik) in front of all services
