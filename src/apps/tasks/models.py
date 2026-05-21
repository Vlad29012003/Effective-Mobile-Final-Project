from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.base import Base


class TaskStatus(StrEnum):
    open = "open"
    in_progress = "in_progress"
    done = "done"


def _now() -> datetime:
    return datetime.now(UTC)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="taskstatus"), default=TaskStatus.open
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    team: Mapped["Team"] = relationship("Team", back_populates="tasks")  # noqa: F821
    assignee: Mapped["User | None"] = relationship(  # noqa: F821
        "User", foreign_keys=[assignee_id]
    )
    comments: Mapped[list["Comment"]] = relationship(  # noqa: F821
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )
    evaluation: Mapped["Evaluation | None"] = relationship(  # noqa: F821
        "Evaluation", back_populates="task", uselist=False, cascade="all, delete-orphan"
    )
