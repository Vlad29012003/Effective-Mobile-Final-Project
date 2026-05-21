from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    def __str__(self) -> str:
        return self.title

    team: Mapped["Team"] = relationship("Team", back_populates="meetings")  # noqa: F821
    creator: Mapped["User"] = relationship("User")  # noqa: F821
