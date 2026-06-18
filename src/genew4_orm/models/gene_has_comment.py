"""GeneHasComment model representing the gene_has_comment table.

This is the junction table for the many-to-many relationship
between Gene and Comment, with editor and date tracking.
"""

from datetime import date
from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.comment import Comment
    from genew4_orm.models.editor import Editor
    from genew4_orm.models.gene import Gene


class GeneHasComment(DeclarativeBase):
    """GeneHasComment junction entity representing the gene_has_comment table.

    This is the junction table for the many-to-many relationship between
    Gene and Comment. It includes an editor reference and date tracking.
    """

    __tablename__ = "gene_has_comment"

    comment_id: Mapped[int] = mapped_column(
        "comment_id",
        Integer,
        ForeignKey("comment.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to comment table",
    )
    hgnc_id: Mapped[int] = mapped_column(
        "hgnc_id",
        Integer,
        ForeignKey("hgnc.hgnc_id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to hgnc (gene) table",
    )
    date_added: Mapped[date] = mapped_column(
        "date_added", Date, default=date.today, nullable=True, comment="Date the comment was linked to the gene"
    )
    editor_id: Mapped[int] = mapped_column(
        "editor_id",
        Integer,
        ForeignKey("editor.ed_id"),
        nullable=False,
        comment="Foreign key to editor table",
    )

    comment: Mapped["Comment"] = relationship(
        back_populates="gene_has_comments",
        foreign_keys="[GeneHasComment.comment_id]",
    )
    gene: Mapped["Gene"] = relationship(
        back_populates="gene_has_comments",
        foreign_keys="[GeneHasComment.hgnc_id]",
    )
    editor: Mapped["Editor"] = relationship(
        foreign_keys="[GeneHasComment.editor_id]",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize a GeneHasComment, applying the SQLModel-parity instantiation default.

        Plain SQLAlchemy 2.0 only applies ``mapped_column(default=...)`` at flush,
        not construction. ``date_added`` defaults to ``date.today()`` at
        instantiation (as SQLModel did), unless explicitly provided.
        """
        if "date_added" not in kwargs:
            self.date_added = date.today()
        super().__init__(**kwargs)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """Return string representation of GeneHasComment."""
        return f"<GeneHasComment(comment_id={self.comment_id}, hgnc_id={self.hgnc_id})>"
