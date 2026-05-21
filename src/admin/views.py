from sqladmin import ModelView

from apps.auth.models import RefreshToken
from apps.comments.models import Comment
from apps.evaluations.models import Evaluation
from apps.meetings.models import Meeting
from apps.tasks.models import Task
from apps.teams.models import Team, TeamMember
from apps.users.models import User


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"

    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.role,
        User.is_active,
        User.created_at,
    ]
    column_labels = {
        "id": "ID",
        "email": "Email",
        "first_name": "Имя",
        "last_name": "Фамилия",
        "role": "Роль",
        "is_active": "Активен",
        "created_at": "Создан",
    }
    # поиск по email, имени, фамилии, роли (#24)
    column_searchable_list = [User.email, User.first_name, User.last_name, User.role]
    column_sortable_list = [User.id, User.email, User.role, User.is_active, User.created_at]
    # #22: password_hash закрыт везде
    column_details_exclude_list = [User.password_hash]
    form_excluded_columns = [User.password_hash, User.created_at, User.updated_at]

    can_create = False
    can_delete = False


class TeamAdmin(ModelView, model=Team):
    name = "Команда"
    name_plural = "Команды"
    icon = "fa-solid fa-people-group"

    column_list = [Team.id, Team.name, Team.description, "creator", Team.join_code, Team.created_at]
    column_labels = {
        "id": "ID",
        "name": "Название",
        "description": "Описание",
        "creator": "Создатель",
        "join_code": "Код входа",
        "created_at": "Создана",
    }
    column_searchable_list = [Team.name, Team.join_code]
    column_sortable_list = [Team.id, Team.name, Team.created_at]
    # #23: системные и авто-поля не редактируются
    form_excluded_columns = [Team.created_at, Team.join_code]

    can_delete = True


class TeamMemberAdmin(ModelView, model=TeamMember):
    name = "Участник команды"
    name_plural = "Участники команд"
    icon = "fa-solid fa-user-group"

    column_list = ["user", "team", TeamMember.role, TeamMember.joined_at]
    column_labels = {
        "user": "Пользователь",
        "team": "Команда",
        "role": "Роль",
        "joined_at": "Добавлен",
    }
    column_sortable_list = [TeamMember.role, TeamMember.joined_at]
    # #23: joined_at — системное поле
    form_excluded_columns = [TeamMember.joined_at]

    can_create = False


class TaskAdmin(ModelView, model=Task):
    name = "Задача"
    name_plural = "Задачи"
    icon = "fa-solid fa-list-check"

    column_list = [
        Task.id,
        Task.title,
        Task.status,
        "team",
        "assignee",
        Task.deadline,
        Task.created_at,
    ]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "status": "Статус",
        "team": "Команда",
        "assignee": "Исполнитель",
        "deadline": "Дедлайн",
        "created_at": "Создана",
    }
    # поиск по названию и статусу (#24)
    column_searchable_list = [Task.title, Task.status]
    column_sortable_list = [Task.id, Task.status, Task.deadline, Task.created_at]
    # #23: системные поля
    form_excluded_columns = [Task.created_at, Task.updated_at]

    can_delete = True


class CommentAdmin(ModelView, model=Comment):
    name = "Комментарий"
    name_plural = "Комментарии"
    icon = "fa-solid fa-comments"

    column_list = ["task", "author", Comment.text, Comment.created_at]
    column_labels = {
        "task": "Задача",
        "author": "Автор",
        "text": "Текст",
        "created_at": "Создан",
    }
    column_searchable_list = [Comment.text]
    column_sortable_list = [Comment.created_at]
    # #23: системные поля
    form_excluded_columns = [Comment.created_at, Comment.updated_at]

    can_create = False


class EvaluationAdmin(ModelView, model=Evaluation):
    name = "Оценка"
    name_plural = "Оценки"
    icon = "fa-solid fa-star"

    column_list = ["task", "evaluator", Evaluation.score, Evaluation.comment, Evaluation.created_at]
    column_labels = {
        "task": "Задача",
        "evaluator": "Оценивающий",
        "score": "Оценка",
        "comment": "Комментарий",
        "created_at": "Дата",
    }
    column_sortable_list = [Evaluation.score, Evaluation.created_at]
    # #23: системные поля
    form_excluded_columns = [Evaluation.created_at]

    can_create = False


class MeetingAdmin(ModelView, model=Meeting):
    name = "Встреча"
    name_plural = "Встречи"
    icon = "fa-solid fa-calendar"

    column_list = [
        Meeting.id,
        Meeting.title,
        "team",
        "creator",
        Meeting.start_at,
        Meeting.end_at,
        Meeting.is_cancelled,
        Meeting.created_at,
    ]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "team": "Команда",
        "creator": "Организатор",
        "start_at": "Начало",
        "end_at": "Конец",
        "is_cancelled": "Отменена",
        "created_at": "Создана",
    }
    # поиск по названию и статусу отмены (#24)
    column_searchable_list = [Meeting.title, Meeting.is_cancelled]
    column_sortable_list = [Meeting.id, Meeting.start_at, Meeting.is_cancelled, Meeting.created_at]
    # #23: системные поля
    form_excluded_columns = [Meeting.created_at]

    can_create = False


class RefreshTokenAdmin(ModelView, model=RefreshToken):
    name = "Refresh Token"
    name_plural = "Refresh Tokens"
    icon = "fa-solid fa-key"

    column_list = ["user", RefreshToken.expires_at, RefreshToken.is_revoked, RefreshToken.created_at]
    column_labels = {
        "user": "Пользователь",
        "expires_at": "Истекает",
        "is_revoked": "Отозван",
        "created_at": "Создан",
    }
    column_sortable_list = [RefreshToken.is_revoked, RefreshToken.expires_at]

    can_create = False
    can_edit = False
