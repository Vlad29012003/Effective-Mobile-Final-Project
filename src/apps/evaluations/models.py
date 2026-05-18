from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (CheckConstraint("score >= 1 AND score <= 5", name="ck_evaluations_score"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), unique=True)
    evaluator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    task: Mapped["Task"] = relationship("Task", back_populates="evaluation")  # noqa: F821
    evaluator: Mapped["User"] = relationship("User")  # noqa: F821
