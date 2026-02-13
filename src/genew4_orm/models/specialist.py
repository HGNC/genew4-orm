"""Specialist model representing the specialist table.

This model contains specialist organization information.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene_group import GeneGroup


class Specialist(SQLModel, table=True):
    """Specialist entity representing the specialist table.

    External specialist organizations that collaborate with HGNC.
    """

    __tablename__ = "specialist"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
    name: str = Field(
        max_length=255,
        nullable=False,
        description="Specialist organization name",
    )
    address: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Specialist organization address",
    )
    url: str | None = Field(
        default=None,
        max_length=255,
        description="Specialist organization website URL",
    )

    # Note: Many-to-many with GeneGroup is through FamHasSpecialist junction table
    # Query via: session.query(Specialist).join(FamHasSpecialist).join(GeneGroup)

    def __repr__(self) -> str:
        """Return string representation of Specialist."""
        return f"<Specialist(id={self.id}, name='{self.name}')>"
