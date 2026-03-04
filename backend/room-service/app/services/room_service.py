"""
app/services/room_service.py — Room Service
────────────────────────────────────────────
All methods are stubs. Implement each one as described in the TODOs.
"""

from uuid import UUID

from app.models.schemas import (
    CreateRoomRequest,
    InviteParticipantRequest,
    JoinRoomResponse,
    ParticipantResponse,
    RoomDetailResponse,
    RoomResponse,
    UpdateRoomRequest,
)


class RoomService:

    # ── Room CRUD ─────────────────────────────────────────────────────────────

    async def create_room(
        self, payload: CreateRoomRequest, owner_id: UUID
    ) -> RoomResponse:
        """
        Create a new whiteboard room.

        TODO:
          1. Persist room record
          2. Add owner as participant with role='owner'
          3. Return RoomResponse
        """
        raise NotImplementedError

    async def get_room(self, room_id: UUID) -> RoomDetailResponse:
        """
        Fetch full room info including participant list.

        TODO: Query DB, raise RoomNotFoundError if missing
        """
        raise NotImplementedError

    async def list_rooms(self, user_id: UUID) -> list[RoomResponse]:
        """
        List all rooms the given user belongs to.

        TODO: Query rooms where user_id is a participant
        """
        raise NotImplementedError

    async def update_room(
        self, room_id: UUID, payload: UpdateRoomRequest, requester_id: UUID
    ) -> RoomResponse:
        """
        Update room metadata. Only owner can update.

        TODO:
          1. Verify requester is owner
          2. Apply partial update
          3. Persist and return updated RoomResponse
        """
        raise NotImplementedError

    async def archive_room(self, room_id: UUID, requester_id: UUID) -> None:
        """
        Soft-delete a room by marking it archived.

        TODO:
          1. Verify requester is owner
          2. Set status='archived'
          3. Optionally notify CRDT service to close open connections
        """
        raise NotImplementedError

    # ── Participants ──────────────────────────────────────────────────────────

    async def join_room(self, room_id: UUID, user_id: UUID) -> JoinRoomResponse:
        """
        Add a user to a room and issue a short-lived WS ticket.

        TODO:
          1. Verify room is active and not full
          2. Upsert participant record
          3. Generate a short-lived signed WS ticket (e.g. 60s JWT)
          4. Return JoinRoomResponse
        """
        raise NotImplementedError

    async def leave_room(self, room_id: UUID, user_id: UUID) -> None:
        """
        Remove a participant from a room.

        TODO:
          1. Delete / mark participant inactive
          2. If owner leaves, optionally transfer ownership or archive
        """
        raise NotImplementedError

    async def invite_participant(
        self,
        room_id: UUID,
        payload: InviteParticipantRequest,
        requester_id: UUID,
    ) -> ParticipantResponse:
        """
        Invite another user and assign a role.

        TODO:
          1. Verify requester has at least editor role
          2. Upsert participant with given role
        """
        raise NotImplementedError

    async def update_participant_role(
        self,
        room_id: UUID,
        target_user_id: UUID,
        new_role: str,
        requester_id: UUID,
    ) -> ParticipantResponse:
        """
        Change a participant's role. Only owner can promote/demote.

        TODO:
          1. Verify requester is owner
          2. Prevent owner from demoting themselves
          3. Persist updated role
        """
        raise NotImplementedError

    async def list_participants(self, room_id: UUID) -> list[ParticipantResponse]:
        """
        Return all participants and their online status.

        TODO: Join participant table with presence data (Redis / in-memory)
        """
        raise NotImplementedError
