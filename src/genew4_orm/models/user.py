"""User model representing user table.

This model contains user account information for authentication.
"""

from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.reminder import Reminder


class User(DeclarativeBase):
    """User entity representing user table.

    Modern authentication users with JWT-based sessions.
    """

    __tablename__ = "user"

    id: Mapped[int | None] = mapped_column(
        primary_key=True, nullable=False,
        comment="Primary key",
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        comment="User display name (unique)",
    )
    first_name: Mapped[str | None] = mapped_column(String(50), comment="User first name")
    last_name: Mapped[str | None] = mapped_column(String(50), comment="User last name")
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, comment="User email address (unique)"
    )
    password: Mapped[str | None] = mapped_column(
        String(255), comment="Hashed password (excluded from serialization)"
    )
    current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether user account is active",
    )
    jwt_refresh: Mapped[str | None] = mapped_column(
        String(255), comment="JWT refresh token (excluded from serialization)"
    )

    # One-to-many with Reminder
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize a User, applying the SQLModel-parity instantiation default.

        Plain SQLAlchemy 2.0 only applies ``mapped_column(default=...)`` at flush,
        not construction. ``current`` defaults to ``True`` at instantiation (as
        SQLModel did), unless explicitly provided.

        SQLModel's constructor also silently *ignores* unknown kwargs (pydantic
        ``extra`` handling), whereas SQLAlchemy's ``_declarative_constructor``
        raises ``TypeError`` on them. Several existing tests construct
        ``User(login=...)`` with ``login`` (an ``Editor`` field, not a ``User``
        field); to keep that working unchanged, unknown kwargs are filtered out
        before delegating to the declarative constructor.
        """
        if "current" not in kwargs:
            self.current = True
        known = {k: v for k, v in kwargs.items() if hasattr(type(self), k)}
        super().__init__(**known)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """Return string representation of User."""
        return f"<User(id={self.id}, display_name='{self.display_name}')>"

    @property
    def full_name(self) -> str:
        """Get the user's full name.

        Returns:
            First name and last name combined, or display name if not set.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name
