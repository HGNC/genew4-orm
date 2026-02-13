"""User model representing user table.

This model contains user account information for authentication.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.reminder import Reminder


class User(SQLModel, table=True):
    """User entity representing user table.

    Modern authentication users with JWT-based sessions.
    """

    __tablename__ = "user"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
    display_name: str = Field(
        max_length=100,
        unique=True,
        description="User display name (unique)",
    )
    first_name: str | None = Field(
        default=None,
        max_length=50,
        description="User first name",
    )
    last_name: str | None = Field(
        default=None,
        max_length=50,
        description="User last name",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        unique=True,
        description="User email address (unique)",
    )
    password: str | None = Field(
        default=None,
        max_length=255,
        description="Hashed password (excluded from serialization)",
    )
    current: bool = Field(
        default=True,
        nullable=False,
        description="Whether user account is active",
    )
    jwt_refresh: str | None = Field(
        default=None,
        max_length=255,
        description="JWT refresh token (excluded from serialization)",
    )

    # One-to-many with Reminder
    reminders: list["Reminder"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )

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
