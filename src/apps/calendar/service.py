from datetime import datetime

from apps.calendar.schemas import CalendarMeetingItem, CalendarResponse, CalendarTaskItem
from apps.meetings.repository import MeetingRepository
from apps.tasks.repository import TaskRepository
from apps.teams.repository import TeamMemberRepository
from packages.errors import BaseError


class NotTeamMemberError(BaseError):
    code = "insufficient_permissions"
    message = "You are not a member of this team"
    status_code = 403


class CalendarService:
    def __init__(
        self,
        task_repo: TaskRepository,
        meeting_repo: MeetingRepository,
        member_repo: TeamMemberRepository,
    ) -> None:
        self._task_repo = task_repo
        self._meeting_repo = meeting_repo
        self._member_repo = member_repo

    async def get_calendar(
        self,
        user_id: int,
        team_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> CalendarResponse:
        if not await self._member_repo.get_member(team_id, user_id):
            raise NotTeamMemberError()

        tasks = await self._task_repo.list_for_team_by_deadline_range(team_id, date_from, date_to)
        meetings = await self._meeting_repo.list_for_team_by_date_range(team_id, date_from, date_to)

        return CalendarResponse(
            tasks=[CalendarTaskItem.model_validate(t) for t in tasks],
            meetings=[CalendarMeetingItem.model_validate(m) for m in meetings],
        )
