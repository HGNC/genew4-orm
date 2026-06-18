"""GeneInfo model for the gene_info table.

Used by coord-builder (NCBI sub-source) and xref-loader (gene_info loader).
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class GeneInfo(DeclarativeBase):
    """NCBI Gene Info record.

    Stores gene information from NCBI including symbols, synonyms,
    chromosome locations, and cross-references.

    Composite primary key: (gi_tax_id, gi_eg_id).
    The PK field names match their column names so that ``mapped_column(primary_key=True, nullable=False)``
    works alongside the other ``mapped_column("...", String)`` fields.
    """

    __tablename__ = "gene_info"

    gi_tax_id: Mapped[str | None] = mapped_column(primary_key=True, nullable=False)
    gi_eg_id: Mapped[str | None] = mapped_column(primary_key=True, nullable=False)
    symbol: Mapped[str | None] = mapped_column("gi_sym", String)
    locus_tag: Mapped[str | None] = mapped_column("gi_locustag", String)
    synonyms: Mapped[str | None] = mapped_column("gi_synonyms", String)
    db_xrefs: Mapped[str | None] = mapped_column("gi_dbxrefs", String)
    chromosome: Mapped[str | None] = mapped_column("gi_chrom", String(255))
    map_location: Mapped[str | None] = mapped_column("gi_map_location", String)
    description: Mapped[str | None] = mapped_column("gi_description", Text)
    type_of_gene: Mapped[str | None] = mapped_column("gi_type_of_gene", String)
    symbol_from_nomenclature_authority: Mapped[str | None] = mapped_column(
        "gi_sym_from_nome_auth", String
    )
    full_name_from_nomenclature_authority: Mapped[str | None] = mapped_column(
        "gi_full_name_from_nome_auth", String
    )
    nomenclature_status: Mapped[str | None] = mapped_column("gi_nome_status", String)
    other_designations: Mapped[str | None] = mapped_column("gi_other_designations", String)
    modification_date: Mapped[str | None] = mapped_column("gi_modification_date", String)
    hgnc_id: Mapped[int | None] = mapped_column("gi_hgnc_id", Integer)
