"""
Демонстрационные данные для TeamFlow.

Запуск:
    python src/seed.py                    # если DATABASE_URL уже в .env
    uv run python src/seed.py             # через uv

Создаёт:
    - 4 пользователя  (admin@example.com / manager@example.com / alice@example.com / bob@example.com)
    - 1 команду       «Команда Альфа»
    - 4 задачи        (разные статусы, исполнители, комментарии)
    - 1 встречу
    - 2 оценки
"""

from __future__ import annotations

import asyncio
import pathlib
import secrets
import sys

# Добавляем src/ в PYTHONPATH, чтобы работали все импорты приложения
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.evaluations.models import Evaluation
from apps.meetings.models import Meeting
from apps.tasks.models import Task, TaskStatus
from apps.teams.models import Team, TeamMember, TeamMemberRole
from apps.users.models import User, UserRole
from configs import settings
from packages.security.passwords import PasswordHasher

HASHER = PasswordHasher()

USERS = [
    {"email": "admin@example.com",   "password": "admin123",   "first_name": "Иван",   "last_name": "Иванов",   "role": UserRole.admin},
    {"email": "manager@example.com", "password": "manager123", "first_name": "Мария",  "last_name": "Петрова",  "role": UserRole.manager},
    {"email": "alice@example.com",   "password": "alice123",   "first_name": "Алиса",  "last_name": "Смирнова", "role": UserRole.user},
    {"email": "bob@example.com",     "password": "bob123",     "first_name": "Борис",  "last_name": "Козлов",   "role": UserRole.user},
]


async def run(session: AsyncSession) -> None:
    now = datetime.now(UTC)

    # ── Пользователи ──────────────────────────────────────────────────────────
    users: list[User] = []
    for u in USERS:
        user = User(
            email=u["email"],
            password_hash=HASHER.hash(u["password"]),
            first_name=u["first_name"],
            last_name=u["last_name"],
            role=u["role"],
        )
        session.add(user)
        users.append(user)
    await session.flush()  # получаем id

    admin_user, manager_user, alice, bob = users

    # ── Команда ───────────────────────────────────────────────────────────────
    team = Team(
        name="Команда Альфа",
        description="Демонстрационная команда для тестирования системы",
        join_code=secrets.token_hex(16),
        created_by=admin_user.id,
    )
    session.add(team)
    await session.flush()

    # ── Участники ─────────────────────────────────────────────────────────────
    members = [
        TeamMember(team_id=team.id, user_id=admin_user.id,   role=TeamMemberRole.admin),
        TeamMember(team_id=team.id, user_id=manager_user.id, role=TeamMemberRole.manager),
        TeamMember(team_id=team.id, user_id=alice.id,        role=TeamMemberRole.member),
        TeamMember(team_id=team.id, user_id=bob.id,          role=TeamMemberRole.member),
    ]
    for m in members:
        session.add(m)
    await session.flush()

    # ── Задачи ────────────────────────────────────────────────────────────────
    tasks = [
        Task(
            title="Настроить CI/CD пайплайн",
            description="Настроить GitHub Actions для автоматической сборки и деплоя",
            status=TaskStatus.done,
            deadline=now - timedelta(days=3),
            team_id=team.id,
            creator_id=manager_user.id,
            assignee_id=admin_user.id,
        ),
        Task(
            title="Разработать модуль авторизации",
            description="JWT-токены, refresh-логика, httpOnly cookies",
            status=TaskStatus.in_progress,
            deadline=now + timedelta(days=5),
            team_id=team.id,
            creator_id=manager_user.id,
            assignee_id=alice.id,
        ),
        Task(
            title="Написать тесты для API задач",
            description="Покрыть тестами CRUD эндпоинты задач с testcontainers",
            status=TaskStatus.open,
            deadline=now + timedelta(days=10),
            team_id=team.id,
            creator_id=manager_user.id,
            assignee_id=bob.id,
        ),
        Task(
            title="Оформить документацию",
            description="README, описание эндпоинтов, инструкция по запуску",
            status=TaskStatus.open,
            deadline=now + timedelta(days=14),
            team_id=team.id,
            creator_id=admin_user.id,
            assignee_id=None,
        ),
    ]
    for t in tasks:
        session.add(t)
    await session.flush()

    done_task, in_progress_task, *_ = tasks

    # ── Комментарии (через ORM напрямую, минуя сервис) ────────────────────────
    from apps.comments.models import Comment

    comments = [
        Comment(task_id=done_task.id,        author_id=admin_user.id,   text="Пайплайн настроен, все стадии проходят."),
        Comment(task_id=done_task.id,        author_id=manager_user.id, text="Отлично! Принято в работу."),
        Comment(task_id=in_progress_task.id, author_id=alice.id,        text="Refresh-логика готова, допиливаю middleware."),
        Comment(task_id=in_progress_task.id, author_id=manager_user.id, text="Не забудь про COOKIE_SECURE в проде."),
    ]
    for c in comments:
        session.add(c)

    # ── Встреча ───────────────────────────────────────────────────────────────
    meeting = Meeting(
        title="Еженедельный синк",
        description="Обсуждение прогресса по задачам",
        team_id=team.id,
        creator_id=manager_user.id,
        start_at=now + timedelta(days=1, hours=10),
        end_at=now + timedelta(days=1, hours=11),
    )
    session.add(meeting)
    await session.flush()

    # ── Оценки ────────────────────────────────────────────────────────────────
    evaluation = Evaluation(
        task_id=done_task.id,
        evaluator_id=manager_user.id,
        score=5,
        comment="Задача выполнена чисто и в срок.",
    )
    session.add(evaluation)

    await session.commit()

    print("\n✓ Демо-данные успешно загружены!\n")
    print("  Пользователи:")
    for u in USERS:
        print(f"    {u['email']:30s}  пароль: {u['password']}")
    print(f"\n  Команда:  «{team.name}»")
    print(f"  Код приглашения: {team.join_code}\n")
    print("  Веб-интерфейс:  http://localhost:8000/web/auth/login")
    print("  Админ-панель:   http://localhost:8000/admin\n")


async def main() -> None:
    db_url = settings.get_database_url()
    if not db_url:
        print("ERROR: DATABASE_URL не задан. Проверьте .env файл.")
        sys.exit(1)

    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Проверяем, не залиты ли данные уже
    async with async_session() as session:
        result = await session.execute(sa.select(sa.func.count()).select_from(User))
        count = result.scalar_one()
        if count > 0:
            print(f"В БД уже есть {count} пользователей. Очистите таблицы перед повторным запуском.")
            print("  docker compose exec db psql -U $DB_USER -d $DB_NAME -c 'TRUNCATE meetings, evaluations, comments, tasks, team_members, teams, refresh_tokens, users RESTART IDENTITY CASCADE;'")
            await engine.dispose()
            return

    async with async_session() as session:
        await run(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
