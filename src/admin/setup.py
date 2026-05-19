from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine

from admin.auth import AdminAuth
from admin.views import (
    CommentAdmin,
    EvaluationAdmin,
    MeetingAdmin,
    RefreshTokenAdmin,
    TaskAdmin,
    TeamAdmin,
    TeamMemberAdmin,
    UserAdmin,
)
from configs import Settings


def setup_admin(app: FastAPI, settings: Settings) -> None:
    engine = create_async_engine(settings.get_database_url(), echo=False)

    auth_backend = AdminAuth(
        username=settings.ADMIN_USERNAME,
        password=settings.ADMIN_PASSWORD,
        secret_key=settings.SESSION_SECRET_KEY or settings.JWT_SECRET_KEY,
    )

    admin = Admin(
        app,
        engine=engine,
        authentication_backend=auth_backend,
        base_url=settings.ADMIN_BASE_PATH,
        title=f"{settings.APP_NAME} Admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TeamMemberAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(EvaluationAdmin)
    admin.add_view(MeetingAdmin)
    admin.add_view(RefreshTokenAdmin)

    @app.on_event("shutdown")
    async def _dispose_admin_engine() -> None:
        await engine.dispose()
