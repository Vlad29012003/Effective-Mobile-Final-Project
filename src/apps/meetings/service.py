from apps.meetings.models import Meeting
from apps.meetings.repository import MeetingRepository
from apps.meetings.schemas import CreateMeetingRequest, UpdateMeetingRequest
from apps.teams.models import TeamMemberRole
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager
from packages.errors import BaseError


class NotTeamMemberError(BaseError):
    code = "insufficient_permissions"
    message = "You are not a member of this team"
    status_code = 403


class InsufficientRoleError(BaseError):
    code = "insufficient_permissions"
    message = "Only admin or manager can manage meetings"
    status_code = 403


class MeetingTimeOverlapError(BaseError):
    code = "time_overlap"
    message = "A meeting already exists in this time slot"
    status_code = 409


class MeetingNotFoundError(BaseError):
    code = "not_found"
    message = "Meeting not found"
    status_code = 404


class MeetingCancelledError(BaseError):
    code = "invalid_state"
    message = "Meeting is already cancelled"
    status_code = 422


class InvalidTimeRangeError(BaseError):
    code = "invalid_input"
    message = "end_at must be after start_at"
    status_code = 422


class MeetingService:
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> None:
        self._meeting_repo = meeting_repo
        self._member_repo = member_repo
        self._tx = tx

    async def _require_member(self, team_id: int, user_id: int) -> None:
        if not await self._member_repo.get_member(team_id, user_id):
            raise NotTeamMemberError()

    async def _require_privileged(self, team_id: int, user_id: int) -> None:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()
        if member.role not in (TeamMemberRole.admin, TeamMemberRole.manager):
            raise InsufficientRoleError()

    async def _get_meeting_for_team(self, meeting_id: int, team_id: int) -> Meeting:
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting or meeting.team_id != team_id:
            raise MeetingNotFoundError()
        return meeting

    async def create_meeting(
        self,
        user_id: int,
        team_id: int,
        data: CreateMeetingRequest,
    ) -> Meeting:
        await self._require_privileged(team_id, user_id)
        if await self._meeting_repo.has_overlap(team_id, data.start_at, data.end_at):
            raise MeetingTimeOverlapError()
        meeting = Meeting(
            title=data.title,
            description=data.description,
            team_id=team_id,
            creator_id=user_id,
            start_at=data.start_at,
            end_at=data.end_at,
        )
        async with self._tx:
            await self._meeting_repo.add(meeting)
        return meeting

    async def list_meetings(self, user_id: int, team_id: int) -> list[Meeting]:
        await self._require_member(team_id, user_id)
        return await self._meeting_repo.list_for_team(team_id)

    async def update_meeting(
        self,
        user_id: int,
        team_id: int,
        meeting_id: int,
        data: UpdateMeetingRequest,
    ) -> Meeting:
        await self._require_privileged(team_id, user_id)
        meeting = await self._get_meeting_for_team(meeting_id, team_id)
        if meeting.is_cancelled:
            raise MeetingCancelledError()

        new_start = data.start_at if data.start_at is not None else meeting.start_at
        new_end = data.end_at if data.end_at is not None else meeting.end_at
        if new_end <= new_start:
            raise InvalidTimeRangeError()

        if await self._meeting_repo.has_overlap(team_id, new_start, new_end, exclude_id=meeting_id):
            raise MeetingTimeOverlapError()

        if data.title is not None:
            meeting.title = data.title
        if data.description is not None:
            meeting.description = data.description
        meeting.start_at = new_start
        meeting.end_at = new_end

        async with self._tx:
            await self._meeting_repo._session.flush()
        return meeting

    async def cancel_meeting(
        self,
        user_id: int,
        team_id: int,
        meeting_id: int,
    ) -> None:
        await self._require_privileged(team_id, user_id)
        meeting = await self._get_meeting_for_team(meeting_id, team_id)
        if meeting.is_cancelled:
            raise MeetingCancelledError()
        meeting.is_cancelled = True
        async with self._tx:
            await self._meeting_repo._session.flush()
