# API Documentation

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

Все защищённые эндпоинты требуют заголовок:
```
Authorization: Bearer <access_token>
```

---

## Аутентификация (`/api/v1/auth`)

### POST `/api/v1/auth/register`
Регистрация нового пользователя.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Тест",
  "last_name": "Тестов"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

**Ошибки:** `409` — email уже занят.

---

### POST `/api/v1/auth/login`
Вход. Возвращает JWT-токены.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response `200`:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Ошибки:** `401` — неверные credentials.

---

### POST `/api/v1/auth/refresh`
Обновление access-токена по refresh-токену.

**Body:**
```json
{ "refresh_token": "eyJ..." }
```

**Response `200`:** новая пара `access_token` / `refresh_token`.

---

### POST `/api/v1/auth/logout`

**Body:**
```json
{ "refresh_token": "eyJ..." }
```

**Response `204`:** нет тела.

---

## Пользователи (`/api/v1/users`) 🔒

### GET `/api/v1/users/me`
Текущий профиль.

**Response `200`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Тест",
  "last_name": "Тестов"
}
```

---

### PATCH `/api/v1/users/me`
Обновление профиля.

**Body (все поля опциональны):**
```json
{
  "first_name": "Тест",
  "last_name": "Тестов"
}
```

---

### POST `/api/v1/users/join`
Вступить в команду по коду приглашения.

**Body:**
```json
{ "join_code": "ABC123" }
```

**Response `200`:** объект `TeamMember`.  
**Ошибки:** `404` — команда не найдена, `409` — уже участник.

---

## Команды (`/api/v1/teams`) 🔒

### POST `/api/v1/teams`
Создать команду. Создатель автоматически становится менеджером.

**Body:**
```json
{
  "name": "Backend Team",
  "description": "Команда разработки"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "name": "Backend Team",
  "description": "Команда разработки",
  "join_code": "X7K2PQ",
  "creator_id": 1
}
```

---

### GET `/api/v1/teams`
Список команд текущего пользователя.

**Response `200`:** массив объектов команды.

---

### GET `/api/v1/teams/{team_id}`
Детали команды. Доступно только участникам.

**Ошибки:** `403` — не участник, `404` — не найдена.

---

### GET `/api/v1/teams/{team_id}/members`
Список участников команды.

**Response `200`:**
```json
[
  {
    "user_id": 1,
    "team_id": 1,
    "role": "manager",
    "joined_at": "2026-05-20T10:00:00Z"
  }
]
```

---

## Задачи (`/api/v1/teams/{team_id}/tasks`) 🔒

### POST `/api/v1/teams/{team_id}/tasks`
Создать задачу. Только менеджер.

**Body:**
```json
{
  "title": "Написать API",
  "description": "Документация + тесты",
  "deadline": "2026-06-01T18:00:00Z",
  "assignee_id": 2
}
```

**Response `201`:**
```json
{
  "id": 1,
  "title": "Написать API",
  "status": "open",
  "team_id": 1,
  "assignee_id": 2,
  "deadline": "2026-06-01T18:00:00Z"
}
```

---

### GET `/api/v1/teams/{team_id}/tasks`
Список задач команды.

**Query params:** `page`, `page_size`, `status` (`open` / `in_progress` / `done`).

---

### GET `/api/v1/teams/{team_id}/tasks/{task_id}`
Детали задачи.

---

### PATCH `/api/v1/teams/{team_id}/tasks/{task_id}`
Обновить задачу. Только менеджер.

**Body (все поля опциональны):**
```json
{
  "title": "Новый заголовок",
  "deadline": "2026-07-01T00:00:00Z"
}
```

---

### PATCH `/api/v1/teams/{team_id}/tasks/{task_id}/status`
Изменить статус задачи. Менеджер — любой статус, участник — только своей задачи.

**Body:**
```json
{ "status": "in_progress" }
```

Допустимые значения: `open`, `in_progress`, `done`.

---

## Комментарии (`/api/v1/teams/{team_id}/tasks/{task_id}/comments`) 🔒

### POST `.../comments`
Добавить комментарий. Любой участник команды.

**Body:**
```json
{ "text": "Взял в работу" }
```

**Response `201`:**
```json
{
  "id": 1,
  "text": "Взял в работу",
  "author_id": 1,
  "task_id": 1,
  "created_at": "2026-05-20T10:00:00Z"
}
```

---

### GET `.../comments`
Список комментариев к задаче.

---

## Оценки (`/api/v1/teams/{team_id}/tasks/{task_id}/evaluation`) 🔒

### POST `.../evaluation`
Оценить выполненную задачу. Только менеджер, задача должна быть в статусе `done`, одна оценка на задачу.

**Body:**
```json
{ "score": 5 }
```

Допустимые значения: `1` – `5`.

**Response `201`:**
```json
{
  "id": 1,
  "score": 5,
  "task_id": 1,
  "evaluator_id": 1
}
```

**Ошибки:** `409` — оценка уже существует, `422` — задача не завершена.

---

### GET `.../evaluation`
Получить оценку задачи. Любой участник команды.

---

## Встречи (`/api/v1/teams/{team_id}/meetings`) 🔒

### POST `/api/v1/teams/{team_id}/meetings`
Запланировать встречу. Только менеджер. Проверяется пересечение с существующими встречами.

**Body:**
```json
{
  "title": "Еженедельный синк",
  "start_at": "2026-05-21T10:00:00Z",
  "end_at": "2026-05-21T11:00:00Z"
}
```

**Response `201`:** объект встречи.  
**Ошибки:** `409` — пересечение по времени, `422` — `end_at` ≤ `start_at`.

---

### GET `/api/v1/teams/{team_id}/meetings`
Список встреч команды.

---

### PATCH `/api/v1/teams/{team_id}/meetings/{meeting_id}`
Обновить встречу. Только менеджер.

---

### DELETE `/api/v1/teams/{team_id}/meetings/{meeting_id}`
Отменить встречу (`is_cancelled = true`). Только менеджер.

---

## Календарь (`/api/v1/teams/{team_id}/calendar`) 🔒

### GET `/api/v1/teams/{team_id}/calendar`
Агрегированный вид задач и встреч за период.

**Query params:**
| Параметр | Формат | Пример |
|---|---|---|
| `date_from` | `YYYY-MM-DDTHH:MM:SSZ` | `2026-05-01T00:00:00Z` |
| `date_to` | `YYYY-MM-DDTHH:MM:SSZ` | `2026-05-31T23:59:59Z` |

**Response `200`:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Написать API",
      "status": "done",
      "deadline": "2026-05-21T18:00:00Z"
    }
  ],
  "meetings": [
    {
      "id": 1,
      "title": "Еженедельный синк",
      "start_at": "2026-05-21T10:00:00Z",
      "end_at": "2026-05-21T11:00:00Z"
    }
  ]
}
```

---

## Ручное тестирование через Swagger

### Шаг 1 — Открыть Swagger
Перейти на `http://localhost:8000/docs`.

### Шаг 2 — Зарегистрироваться
`POST /api/v1/auth/register` → выполнить с телом выше → `201 Created`.

### Шаг 3 — Войти и получить токен
`POST /api/v1/auth/login` → скопировать `access_token`.

### Шаг 4 — Авторизоваться в Swagger
Нажать кнопку **Authorize** (замок вверху) → вставить токен → **Authorize**.

### Шаг 5 — Создать команду
`POST /api/v1/teams` → получить `join_code` в ответе.

### Шаг 6 — Проверить цепочку
```
Создать задачу → GET задачи → PATCH статус на in_progress
→ PATCH статус на done → POST оценку → GET оценку
```

### Шаг 7 — Встречи и Calendar
```
POST /meetings (с корректным диапазоном времени)
→ POST /meetings (с пересекающимся временем) → ожидаем 409
→ GET /calendar?date_from=...&date_to=... → видим задачу и встречу
```

### Шаг 8 — Refresh и Logout
```
POST /auth/refresh (с refresh_token из шага 3)
→ POST /auth/logout (инвалидировать токен)
→ POST /auth/refresh снова → ожидаем 401
```

---

## Коды ошибок

| Код | Значение |
|---|---|
| `400` | Некорректный запрос |
| `401` | Не авторизован / токен истёк |
| `403` | Нет доступа (не участник / не менеджер) |
| `404` | Ресурс не найден |
| `409` | Конфликт (email занят, оценка уже есть, пересечение встреч) |
| `422` | Ошибка валидации (неверный формат данных) |
