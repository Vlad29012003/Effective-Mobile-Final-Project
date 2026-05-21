from datetime import datetime
from pathlib import Path

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Form, Request
from pydantic import ValidationError
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.comments.schemas import CreateCommentRequest
from apps.comments.service import CommentService
from apps.meetings.schemas import CreateMeetingRequest
from apps.meetings.service import MeetingService
from apps.tasks.models import TaskStatus
from apps.tasks.schemas import CreateTaskRequest, UpdateTaskRequest
from apps.tasks.service import TaskService
from apps.teams.service import TeamService
from packages.errors import BaseError
from presentations.web.deps import get_web_user

router = APIRouter(tags=["Web:Teams"])
router.route_class = DishkaRoute

_templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/teams/{team_id}")
async def team_detail(
    request: Request,
    team_id: int,
    team_service: FromDishka[TeamService],
    task_service: FromDishka[TaskService],
    comment_service: FromDishka[CommentService],
    meeting_service: FromDishka[MeetingService],
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)

    user_id = int(user["sub"])
    try:
        team = await team_service.get_team(team_id, user_id)
        members = await team_service.get_members(team_id, user_id)
        tasks = await task_service.list_tasks(user_id, team_id)
        meetings = await meeting_service.list_meetings(user_id, team_id)
    except BaseError:
        return RedirectResponse("/web/dashboard?error=Команда+не+найдена", status_code=303)

    active_tab = request.query_params.get("tab", "tasks")
    task_id = request.query_params.get("task_id")
    comments = []
    selected_task = None
    if task_id:
        try:
            task_id_int = int(task_id)
            selected_task = next((t for t in tasks if t.id == task_id_int), None)
            if selected_task:
                comments = await comment_service.list_comments(user_id, team_id, task_id_int)
        except Exception:
            pass

    return _templates.TemplateResponse(
        request,
        "teams/detail.html",
        {
            "user": user,
            "team": team,
            "members": members,
            "tasks": tasks,
            "meetings": meetings,
            "active_tab": active_tab,
            "selected_task": selected_task,
            "comments": comments,
            "TaskStatus": TaskStatus,
            "error": request.query_params.get("error"),
            "success": request.query_params.get("success"),
        },
    )


@router.post("/teams/{team_id}/tasks")
async def create_task(
    request: Request,
    team_id: int,
    service: FromDishka[TaskService],
    title: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(""),
    assignee_id: str = Form(""),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        deadline_dt = datetime.fromisoformat(deadline) if deadline else None
        assignee = int(assignee_id) if assignee_id else None
        await service.create_task(
            int(user["sub"]),
            team_id,
            CreateTaskRequest(
                title=title,
                description=description or None,
                deadline=deadline_dt,
                assignee_id=assignee,
            ),
        )
        return RedirectResponse(
            f"/web/teams/{team_id}?tab=tasks&success=Задача+создана", status_code=303
        )
    except BaseError as e:
        return RedirectResponse(
            f"/web/teams/{team_id}?tab=tasks&error={e.message}", status_code=303
        )


@router.post("/teams/{team_id}/tasks/{task_id}/status")
async def change_task_status(
    request: Request,
    team_id: int,
    task_id: int,
    service: FromDishka[TaskService],
    status: str = Form(...),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        await service.change_status(int(user["sub"]), team_id, task_id, TaskStatus(status))
    except BaseError:
        pass
    return RedirectResponse(f"/web/teams/{team_id}?tab=tasks", status_code=303)


@router.post("/teams/{team_id}/tasks/{task_id}/comments")
async def add_comment(
    request: Request,
    team_id: int,
    task_id: int,
    service: FromDishka[CommentService],
    text: str = Form(...),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        await service.add_comment(
            int(user["sub"]),
            team_id,
            task_id,
            CreateCommentRequest(text=text),
        )
    except BaseError:
        pass
    return RedirectResponse(f"/web/teams/{team_id}?tab=tasks&task_id={task_id}", status_code=303)


@router.post("/teams/{team_id}/tasks/{task_id}/assignee")
async def update_task_assignee(
    request: Request,
    team_id: int,
    task_id: int,
    service: FromDishka[TaskService],
    assignee_id: str = Form(""),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    assignee = int(assignee_id) if assignee_id else None
    try:
        await service.update_task(
            int(user["sub"]),
            team_id,
            task_id,
            UpdateTaskRequest(assignee_id=assignee),
        )
    except BaseError:
        pass
    return RedirectResponse(
        f"/web/teams/{team_id}?tab=tasks&task_id={task_id}", status_code=303
    )


@router.post("/teams/{team_id}/tasks/{task_id}/delete")
async def delete_task_web(
    request: Request,
    team_id: int,
    task_id: int,
    service: FromDishka[TaskService],
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        await service.delete_task(int(user["sub"]), team_id, task_id)
    except BaseError:
        pass
    return RedirectResponse(f"/web/teams/{team_id}?tab=tasks", status_code=303)


@router.post("/teams/{team_id}/meetings")
async def create_meeting(
    request: Request,
    team_id: int,
    service: FromDishka[MeetingService],
    title: str = Form(...),
    start_at: str = Form(...),
    end_at: str = Form(...),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        meeting_data = CreateMeetingRequest(
            title=title,
            start_at=datetime.fromisoformat(start_at),
            end_at=datetime.fromisoformat(end_at),
        )
        await service.create_meeting(int(user["sub"]), team_id, meeting_data)
        return RedirectResponse(
            f"/web/teams/{team_id}?tab=meetings&success=Встреча+создана", status_code=303
        )
    except BaseError as e:
        return RedirectResponse(
            f"/web/teams/{team_id}?tab=meetings&error={e.message}", status_code=303
        )
    except (ValidationError, ValueError):
        return RedirectResponse(
            f"/web/teams/{team_id}?tab=meetings&error=Дата+окончания+должна+быть+позже+начала",
            status_code=303,
        )
