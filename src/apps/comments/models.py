from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    def __str__(self) -> str:
        return self.text[:60] + ("…" if len(self.text) > 60 else "")

    task: Mapped["Task"] = relationship("Task", back_populates="comments")  # noqa: F821
    author: Mapped["User"] = relationship("User")  # noqa: F821
