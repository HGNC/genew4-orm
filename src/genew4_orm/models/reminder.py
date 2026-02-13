"""Reminder model representing the reminder table.

This model contains user reminder/task information.
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene import Gene
    from genew4_orm.models.gene_group import GeneGroup
    from genew4_orm.models.user import User


class Reminder(SQLModel, table=True):
    """Reminder entity representing the reminder table.

    User reminders and tasks that can be linked to genes or gene groups.
    """

    __tablename__ = "reminder"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
    subject: str = Field(
        max_length=255,
        description="Reminder subject/title",
    )
    content: str = Field(
        sa_column=Column(String),  # Using String with Text type
        description="Reminder content/body",
    )
    reminder_date: date = Field(
        sa_column=Column("date", Date),
        description="Due date for the reminder",
    )
    sent: bool = Field(
        default=False,
        description="Whether the reminder has been sent",
    )

    # Foreign keys and relationships
    user_id: int | None = Field(
        default=None,
        sa_column=Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE")),
        description="Foreign key to user table",
    )
    user: "User" = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={
            "foreign_keys": "[Reminder.user_id]",
        },
    )

    hgnc_id: int | None = Field(
        default=None,
        sa_column=Column("hgnc_id", Integer, ForeignKey("hgnc.hgnc_id", ondelete="CASCADE")),
        description="Foreign key to hgnc (gene) table",
    )
    gene: "Gene" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Reminder.hgnc_id]",
        },
    )

    group_id: int | None = Field(
        default=None,
        sa_column=Column("group_id", Integer, ForeignKey("family_new.id", ondelete="CASCADE")),
        description="Foreign key to family_new (gene group) table",
    )
    gene_group: "GeneGroup" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Reminder.group_id]",
        },
    )

    def __repr__(self) -> str:
        """Return string representation of Reminder."""
        return f"<Reminder(id={self.id}, subject='{self.subject}')>"
