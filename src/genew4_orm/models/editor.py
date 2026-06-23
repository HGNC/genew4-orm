"""Editor model representing the editor table.

This model contains legacy editor user information.
"""

from db_common import DeclarativeBase
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Editor(DeclarativeBase):
    """Editor entity representing the editor table.

    Legacy editor users from the previous system.
    """

    __tablename__ = "editor"

    id: Mapped[int | None] = mapped_column(
        "ed_id",
        Integer,
        primary_key=True,
        nullable=False,
        comment="Primary key",
    )
    full_name: Mapped[str | None] = mapped_column(
        "ed_full_name",
        String,
        comment="Editor full name",
    )
    password: Mapped[str | None] = mapped_column(
        "ed_passwd",
        String,
        comment="Editor password (hashed)",
    )
    preferences: Mapped[str | None] = mapped_column(
        "ed_pref",
        String,
        comment="Editor preferences",
    )
    editor: Mapped[str | None] = mapped_column(
        "ed_login",
        String,
        comment="Editor login name",
    )
    current: Mapped[bool] = mapped_column(
        "ed_active",
        Boolean,
        default=True,
        comment="Whether editor account is active",
    )

    def __repr__(self) -> str:
        """Return string representation of Editor."""
        return f"<Editor(id={self.id}, editor='{self.editor}')>"
