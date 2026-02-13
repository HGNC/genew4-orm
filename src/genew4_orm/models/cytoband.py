"""Cytoband data class representing the cytoband table.

This module provides a data class for cytogenetic band data.
Note: The cytoband table has no primary key in the database schema.
All columns are nullable and there are no unique constraints.
This model cannot be used as a full ORM-mapped model due to lack of primary key.
Use raw SQL queries for CRUD operations on this table.
"""

from dataclasses import dataclass

from genew4_orm.enums import CytobandSourceType


@dataclass
class Cytoband:
    """Data class for cytoband table records.

    Cytogenetic band data from UCSC/Ensembl sources.
    Note: This table has no primary key in the database schema.
    Use raw SQL queries for CRUD operations.

    Attributes:
        source: Data source (UCSC or Ensembl)
        chromosome: Chromosome name
        start: Start position
        end: End position
        band: Cytogenetic band name
        stain: Band stain type
    """

    source: CytobandSourceType | None
    chromosome: str | None
    start: int | None
    end: int | None
    band: str | None
    stain: str | None

    def __repr__(self) -> str:
        """Return string representation of Cytoband."""
        return (
            f"<Cytoband(source={self.source}, chromosome='{self.chromosome}', "
            f"band='{self.band}')>"
        )
