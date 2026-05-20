"""GeneHasComment model representing the gene_has_comment table.

This is the junction table for the many-to-many relationship
between Gene and Comment, with editor and date tracking.
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.comment import Comment
    from genew4_orm.models.editor import Editor
    from genew4_orm.models.gene import Gene


class GeneHasComment(SQLModel, table=True):
    """GeneHasComment junction entity representing the gene_has_comment table.

    This is the junction table for the many-to-many relationship between
    Gene and Comment. It includes an editor reference and date tracking.
    """

    __tablename__ = "gene_has_comment"

    comment_id: int = Field(
        sa_column=Column(
            "comment_id",
            Integer,
            ForeignKey("comment.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to comment table",
    )
    hgnc_id: int = Field(
        sa_column=Column(
            "hgnc_id",
            Integer,
            ForeignKey("hgnc.hgnc_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to hgnc (gene) table",
    )
    date_added: date = Field(
        default_factory=date.today,
        sa_column=Column("date_added", Date, default=date.today),
        description="Date the comment was linked to the gene",
    )
    editor_id: int = Field(
        sa_column=Column(
            "editor_id",
            Integer,
            ForeignKey("editor.ed_id"),
            nullable=False,
        ),
        description="Foreign key to editor table",
    )

    comment: "Comment" = Relationship(
        back_populates="gene_has_comments",
        sa_relationship_kwargs={
            "foreign_keys": "[GeneHasComment.comment_id]",
        },
    )
    gene: "Gene" = Relationship(
        back_populates="gene_has_comments",
        sa_relationship_kwargs={
            "foreign_keys": "[GeneHasComment.hgnc_id]",
        },
    )
    editor: "Editor" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[GeneHasComment.editor_id]",
        },
    )

    def __repr__(self) -> str:
        """Return string representation of GeneHasComment."""
        return f"<GeneHasComment(comment_id={self.comment_id}, hgnc_id={self.hgnc_id})>"
