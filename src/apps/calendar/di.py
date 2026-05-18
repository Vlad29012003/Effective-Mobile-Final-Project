from dishka import Provider, Scope, provide

from apps.calendar.service import CalendarService
from apps.meetings.repository import MeetingRepository
from apps.tasks.repository import TaskRepository
from apps.teams.repository import TeamMemberRepository


class CalendarProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def calendar_service(
        self,
        task_repo: TaskRepository,
        meeting_repo: MeetingRepository,
        member_repo: TeamMemberRepository,
    ) -> CalendarService:
        return CalendarService(task_repo, meeting_repo, member_repo)


provider = CalendarProvider()
