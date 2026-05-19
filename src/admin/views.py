from sqladmin import ModelView

from apps.auth.models import RefreshToken
from apps.comments.models import Comment
from apps.evaluations.models import Evaluation
from apps.meetings.models import Meeting
from apps.tasks.models import Task
from apps.teams.models import Team, TeamMember
from apps.users.models import User


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"

    column_list = [User.id, User.email, User.first_name, User.last_name, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    column_sortable_list = [User.id, User.email, User.role, User.is_active, User.created_at]
    column_details_exclude_list = [User.password_hash]

    can_create = False
    can_delete = False


class TeamAdmin(ModelView, model=Team):
    name = "Team"
    name_plural = "Teams"
    icon = "fa-solid fa-people-group"

    column_list = [Team.id, Team.name, Team.join_code, Team.created_by, Team.created_at]
    column_searchable_list = [Team.name, Team.join_code]
    column_sortable_list = [Team.id, Team.name, Team.created_at]

    can_delete = True


class TeamMemberAdmin(ModelView, model=TeamMember):
    name = "Team Member"
    name_plural = "Team Members"
    icon = "fa-solid fa-user-group"

    column_list = [TeamMember.id, TeamMember.team_id, TeamMember.user_id, TeamMember.role, TeamMember.joined_at]
    column_sortable_list = [TeamMember.id, TeamMember.role, TeamMember.joined_at]

    can_create = False


class TaskAdmin(ModelView, model=Task):
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-list-check"

    column_list = [Task.id, Task.title, Task.status, Task.team_id, Task.assignee_id, Task.deadline, Task.created_at]
    column_searchable_list = [Task.title]
    column_sortable_list = [Task.id, Task.status, Task.deadline, Task.created_at]

    can_delete = True


class CommentAdmin(ModelView, model=Comment):
    name = "Comment"
    name_plural = "Comments"
    icon = "fa-solid fa-comments"

    column_list = [Comment.id, Comment.task_id, Comment.author_id, Comment.text, Comment.created_at]
    column_sortable_list = [Comment.id, Comment.task_id, Comment.created_at]

    can_create = False


class EvaluationAdmin(ModelView, model=Evaluation):
    name = "Evaluation"
    name_plural = "Evaluations"
    icon = "fa-solid fa-star"

    column_list = [Evaluation.id, Evaluation.task_id, Evaluation.evaluator_id, Evaluation.score, Evaluation.created_at]
    column_sortable_list = [Evaluation.id, Evaluation.score, Evaluation.created_at]

    can_create = False


class MeetingAdmin(ModelView, model=Meeting):
    name = "Meeting"
    name_plural = "Meetings"
    icon = "fa-solid fa-calendar"

    column_list = [Meeting.id, Meeting.title, Meeting.team_id, Meeting.start_at, Meeting.end_at, Meeting.is_cancelled, Meeting.created_at]
    column_searchable_list = [Meeting.title]
    column_sortable_list = [Meeting.id, Meeting.start_at, Meeting.is_cancelled, Meeting.created_at]

    can_create = False


class RefreshTokenAdmin(ModelView, model=RefreshToken):
    name = "Refresh Token"
    name_plural = "Refresh Tokens"
    icon = "fa-solid fa-key"

    column_list = [RefreshToken.id, RefreshToken.user_id, RefreshToken.expires_at, RefreshToken.is_revoked, RefreshToken.created_at]
    column_sortable_list = [RefreshToken.id, RefreshToken.is_revoked, RefreshToken.expires_at]

    can_create = False
    can_edit = False
