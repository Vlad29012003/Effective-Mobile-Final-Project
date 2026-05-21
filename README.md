# TeamFlow

REST API + веб-интерфейс для управления командами и задачами. Построен на FastAPI с асинхронной архитектурой, покрыт интеграционными тестами и упакован в Docker.

## Возможности

- Регистрация и аутентификация через JWT (access + refresh токены в httpOnly cookie)
- Управление командами: создание, вступление по коду приглашения, роли (manager / member)
- Задачи: создание, назначение исполнителя, смена статуса (open → in_progress → done), дедлайн
- Комментарии к задачам
- Оценки выполненных задач (1–5 баллов, только для завершённых задач)
- Встречи: планирование с проверкой пересечения по времени
- Календарь: агрегированный вид задач и встреч по диапазону дат
- Веб-интерфейс на Jinja2 + Bootstrap 5
- Административная панель (SQLAdmin)
- Структурированное логирование (JSON в prod, text в dev)
- Трассировка запросов через `X-Trace-Id`
- Интеграция с Sentry (опционально)

## Технологии

| Слой | Технология |
|---|---|
| Web framework | FastAPI 0.116+ |
| ORM | SQLAlchemy 2.0 async (Mapped / mapped_column) |
| База данных | PostgreSQL 17 |
| Миграции | Alembic |
| Dependency Injection | Dishka |
| Конфигурация | pydantic-settings |
| Аутентификация | PyJWT (HS256) |
| Кеширование | Redis 8 |
| Шаблоны | Jinja2 + Bootstrap 5 |
| Админка | SQLAdmin |
| Тесты | pytest-asyncio + testcontainers |
| Контейнеризация | Docker + Docker Compose |
| Линтер | Ruff |

## Архитектура

```
src/
├── apps/               # Бизнес-логика по доменам
│   ├── auth/           # Регистрация, логин, refresh, logout
│   ├── users/          # Профиль, вступление в команду
│   ├── teams/          # Команды, участники
│   ├── tasks/          # Задачи
│   ├── comments/       # Комментарии
│   ├── evaluations/    # Оценки задач
│   ├── meetings/       # Встречи
│   └── calendar/       # Агрегированный календарь
│
├── presentations/
│   ├── api/            # REST роутеры, exception handlers, middlewares
│   └── web/            # Jinja2 роутеры, шаблоны, static
│
├── admin/              # SQLAdmin: views, auth backend, setup
├── di/                 # DI-провайдеры инфраструктуры (DB, Redis, JWT, ...)
├── packages/           # Переиспользуемые утилиты (jwt, passwords, db, logging)
├── configs/            # pydantic-settings singleton
├── framework/          # AppRegistry, discovery (авто-регистрация приложений)
├── startup/            # Фабрика FastAPI приложения
└── tests/              # Интеграционные тесты
```

### Ключевые паттерны

**AppConfig registry** — каждое приложение (например `apps/tasks/apps.py`) реализует `AppConfig.install()`, который регистрирует роутер и DI-провайдер в общем реестре. Фабрика в `startup/api.py` обходит все приложения через `discover_app_paths()` и собирает их без явного перечисления.

**Repository + Service** — `BaseRepository[ModelT]` содержит базовые CRUD-операции через SQLAlchemy async session. Сервисы оркестрируют репозитории и инкапсулируют бизнес-правила (проверка членства, конфликты встреч, уникальность оценок).

**TransactionManager** — обёртка над сессией, используется в сервисах для явного `commit` / `rollback`. DI-контейнер (Dishka) управляет временем жизни сессии в рамках запроса (`Scope.REQUEST`).

**POST-Redirect-GET** — все формы веб-интерфейса после успешной обработки делают `303 See Other` редирект, что исключает повторную отправку при F5.

## Быстрый старт (Docker)

```bash
git clone <repo-url>
cd final-project

# Добавить env в директории 
final-project

# Пример .env файла

DB_HOST=localhost
DB_PORT=5433
DB_USER=app
DB_PASSWORD=app
DB_NAME=app
SYNC_DB_DRIVER=postgresql+psycopg2


# Запустить всё (db + redis + migrate + app)
docker compose up --build
```

Приложение поднимется на **http://localhost:8000**.
Web будет по адресу http://localhost:8000/web/auth/login


## Маршруты

| Интерфейс | URL | Описание |
|---|---|---|
| REST API | `/api/v1/...` | JSON API |
| Swagger UI | `/docs` | Интерактивная документация |
| ReDoc | `/redoc` | Альтернативная документация |
| Админ-панель | `/admin` | SQLAdmin (логин: `ADMIN_USERNAME`, пароль: `ADMIN_PASSWORD` из `.env`) |

## Тесты

Требования: Python 3.13+, Docker (для testcontainers), установленные dev-зависимости.

```bash
# 1. Установить зависимости (один раз)
pip install "testcontainers[postgres]>=4.8.1" pytest pytest-asyncio httpx psycopg2-binary
pip install -e .

# 2. Запустить тесты из корня проекта
pytest src/tests/ -v
```

Если используется `uv`:
```bash
uv run pytest src/tests/ -v
```

Тесты используют **testcontainers** — PostgreSQL поднимается автоматически в отдельном Docker-контейнере, Alembic-миграции накатываются перед запуском, после каждого теста таблицы очищаются через `TRUNCATE ... CASCADE`. Запущенный `docker-compose` для тестов не нужен.

Покрытие: 29 тестов по 6 модулям (auth, teams, tasks, comments, evaluations, meetings).

## Демонстрационные данные

После `docker compose up` можно залить тестовые данные:

```bash
docker compose exec app python src/seed.py
```

Скрипт создаст 4 пользователя, команду, задачи, встречу и оценки:

| Email | Пароль | Роль |
|---|---|---|
| admin@example.com | admin123 | Администратор |
| manager@example.com | manager123 | Менеджер |
| alice@example.com | alice123 | Участник |
| bob@example.com | bob123 | Участник |

## Административная панель

Доступна по адресу **http://localhost:8000/admin**.

Логин и пароль задаются в `.env`:
```env
ADMIN_USERNAME=admin   # по умолчанию: admin
ADMIN_PASSWORD=admin   # по умолчанию: admin
```

> В продакшене обязательно задайте надёжный пароль через переменные окружения.

## Документация

- [docs/api.md](docs/api.md) — описание всех эндпоинтов и план тестирования API
- [docs/frontend.md](docs/frontend.md) — руководство по веб-интерфейсу
