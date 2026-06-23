"""Comment model representing the comment table.

This model contains comment information with publication workflow
status tracking and self-referencing replacement links.
"""

from datetime import date
from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from genew4_orm.enums import PublishStatus, enum_field

if TYPE_CHECKING:
    from genew4_orm.models.editor import Editor
    from genew4_orm.models.gene_has_comment import GeneHasComment


class Comment(DeclarativeBase):
    """Comment entity representing the comment table.

    Stores user comments with a publication workflow (pending/published/rejected),
    author and publisher tracking, and self-referencing replacement links.
    """

    __tablename__ = "comment"

    id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Primary key (auto-increment via comment_sequence)",
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False, comment="Comment text content")
    author_id: Mapped[int] = mapped_column(
        "author_id",
        Integer,
        ForeignKey("editor.ed_id"),
        nullable=False,
        comment="Foreign key to editor table (comment author)",
    )
    lock: Mapped[str | None] = mapped_column("lock", String, comment="Editing lock")
    created: Mapped[date | None] = mapped_column(
        "created", Date, default=date.today, comment="Date comment was created"
    )
    publisher_id: Mapped[int | None] = mapped_column(
        "publisher_id",
        Integer,
        ForeignKey("editor.ed_id"),
        comment="Foreign key to editor table (comment publisher)",
    )
    status: Mapped[str] = enum_field(
        PublishStatus,
        default=PublishStatus.PENDING,
        nullable=False,
        column_name="status",
    )
    status_date: Mapped[date | None] = mapped_column(
        "status_date", Date, default=date.today, comment="Date of last status change"
    )
    replace_id: Mapped[int | None] = mapped_column(
        "replace_id",
        Integer,
        ForeignKey("comment.id"),
        comment="Foreign key to comment table (comment this replaces)",
    )
    replacement_id: Mapped[int | None] = mapped_column(
        "replacement_id",
        Integer,
        ForeignKey("comment.id"),
        comment="Foreign key to comment table (replacement comment)",
    )

    author: Mapped["Editor"] = relationship(
        foreign_keys="[Comment.author_id]",
    )
    publisher: Mapped["Editor"] = relationship(
        foreign_keys="[Comment.publisher_id]",
    )
    gene_has_comments: Mapped[list["GeneHasComment"]] = relationship(
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize a Comment, applying the SQLModel-parity instantiation default.

        Plain SQLAlchemy 2.0 only applies ``mapped_column(default=...)`` at flush,
        not construction. ``status`` defaults to ``PublishStatus.PENDING`` at
        instantiation (as SQLModel did), unless explicitly provided.
        """
        if "status" not in kwargs:
            self.status = PublishStatus.PENDING
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Return string representation of Comment."""
        return f"<Comment(id={self.id})>"
