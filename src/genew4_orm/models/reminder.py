"""Reminder model representing the reminder table.

This model contains user reminder/task information.
"""

from datetime import date
from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.gene import Gene
    from genew4_orm.models.gene_group import GeneGroup
    from genew4_orm.models.user import User


class Reminder(DeclarativeBase):
    """Reminder entity representing the reminder table.

    User reminders and tasks that can be linked to genes or gene groups.
    """

    __tablename__ = "reminder"

    id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Primary key",
    )
    subject: Mapped[str] = mapped_column(String(255), comment="Reminder subject/title")
    content: Mapped[str] = mapped_column(
        String, nullable=True, comment="Reminder content/body"
    )  # Using String with Text type
    reminder_date: Mapped[date] = mapped_column("date", Date, nullable=True, comment="Due date for the reminder")
    sent: Mapped[bool] = mapped_column(Boolean, default=False, comment="Whether the reminder has been sent")

    # Foreign keys and relationships
    user_id: Mapped[int | None] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        comment="Foreign key to user table",
    )
    user: Mapped["User"] = relationship(
        back_populates="reminders",
        foreign_keys="[Reminder.user_id]",
    )

    hgnc_id: Mapped[int | None] = mapped_column(
        "hgnc_id",
        Integer,
        ForeignKey("hgnc.hgnc_id", ondelete="CASCADE"),
        comment="Foreign key to hgnc (gene) table",
    )
    gene: Mapped["Gene"] = relationship(
        foreign_keys="[Reminder.hgnc_id]",
    )

    group_id: Mapped[int | None] = mapped_column(
        "group_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        comment="Foreign key to family_new (gene group) table",
    )
    gene_group: Mapped["GeneGroup"] = relationship(
        foreign_keys="[Reminder.group_id]",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize a Reminder, applying the SQLModel-parity instantiation default.

        Plain SQLAlchemy 2.0 only applies ``mapped_column(default=...)`` at flush,
        not construction. ``sent`` defaults to ``False`` at instantiation (as
        SQLModel did), unless explicitly provided.
        """
        if "sent" not in kwargs:
            self.sent = False
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Return string representation of Reminder."""
        return f"<Reminder(id={self.id}, subject='{self.subject}')>"
