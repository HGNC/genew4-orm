"""Editor model representing the editor table.

This model contains legacy editor user information.
"""

from sqlmodel import Field, SQLModel


class Editor(SQLModel, table=True):
    """Editor entity representing the editor table.

    Legacy editor users from the previous system.
    """

    __tablename__ = "editor"

    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "ed_id"},
        description="Primary key",
    )
    full_name: str | None = Field(
        default=None,
        sa_column_kwargs={"name": "ed_full_name"},
        description="Editor full name",
    )
    password: str | None = Field(
        default=None,
        sa_column_kwargs={"name": "ed_passwd"},
        description="Editor password (hashed)",
    )
    preferences: str | None = Field(
        default=None,
        sa_column_kwargs={"name": "ed_pref"},
        description="Editor preferences",
    )
    editor: str | None = Field(
        default=None,
        sa_column_kwargs={"name": "ed_login"},
        description="Editor login name",
    )
    current: bool = Field(
        default=True,
        sa_column_kwargs={"name": "ed_active"},
        description="Whether editor account is active",
    )

    def __repr__(self) -> str:
        """Return string representation of Editor."""
        return f"<Editor(id={self.id}, editor='{self.editor}')>"
