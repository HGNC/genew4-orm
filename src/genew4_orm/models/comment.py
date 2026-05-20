"""Comment model representing the comment table.

This model contains comment information with publication workflow
status tracking and self-referencing replacement links.
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlmodel import Field, Relationship, SQLModel

from genew4_orm.enums import PublishStatus, enum_field

if TYPE_CHECKING:
    from genew4_orm.models.editor import Editor
    from genew4_orm.models.gene_has_comment import GeneHasComment


class Comment(SQLModel, table=True):
    """Comment entity representing the comment table.

    Stores user comments with a publication workflow (pending/published/rejected),
    author and publisher tracking, and self-referencing replacement links.
    """

    __tablename__ = "comment"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key (auto-increment via comment_sequence)",
    )
    comment: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Comment text content",
    )
    author_id: int = Field(
        sa_column=Column("author_id", Integer, ForeignKey("editor.ed_id"), nullable=False),
        description="Foreign key to editor table (comment author)",
    )
    lock: str | None = Field(
        default=None,
        sa_column=Column("lock", String),
        description="Editing lock",
    )
    created: date | None = Field(
        default_factory=date.today,
        sa_column=Column("created", Date, default=date.today),
        description="Date comment was created",
    )
    publisher_id: int | None = Field(
        default=None,
        sa_column=Column("publisher_id", Integer, ForeignKey("editor.ed_id")),
        description="Foreign key to editor table (comment publisher)",
    )
    status: str = enum_field(
        PublishStatus,
        default=PublishStatus.PENDING,
        nullable=False,
        column_name="status",
    )
    status_date: date | None = Field(
        default_factory=date.today,
        sa_column=Column("status_date", Date, default=date.today),
        description="Date of last status change",
    )
    replace_id: int | None = Field(
        default=None,
        sa_column=Column("replace_id", Integer, ForeignKey("comment.id")),
        description="Foreign key to comment table (comment this replaces)",
    )
    replacement_id: int | None = Field(
        default=None,
        sa_column=Column("replacement_id", Integer, ForeignKey("comment.id")),
        description="Foreign key to comment table (replacement comment)",
    )

    author: "Editor" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Comment.author_id]",
        },
    )
    publisher: "Editor" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Comment.publisher_id]",
        },
    )
    gene_has_comments: list["GeneHasComment"] = Relationship(
        back_populates="comment",
        cascade_delete=True,
    )

    def __repr__(self) -> str:
        """Return string representation of Comment."""
        return f"<Comment(id={self.id})>"
