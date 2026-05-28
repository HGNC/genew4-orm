"""GeneInfo model for the gene_info table.

Used by coord-builder (NCBI sub-source) and xref-loader (gene_info loader).
"""

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, SQLModel


class GeneInfo(SQLModel, table=True):
    """NCBI Gene Info record.

    Stores gene information from NCBI including symbols, synonyms,
    chromosome locations, and cross-references.

    Composite primary key: (gi_tax_id, gi_eg_id).
    The PK field names match their column names so that SQLModel's
    Field(primary_key=True) mechanism works alongside sa_column fields.
    """

    __tablename__ = "gene_info"

    gi_tax_id: str | None = Field(default=None, primary_key=True)
    gi_eg_id: str | None = Field(default=None, primary_key=True)
    symbol: str | None = Field(default=None, sa_column=Column("gi_sym", String))
    locus_tag: str | None = Field(default=None, sa_column=Column("gi_locustag", String))
    synonyms: str | None = Field(default=None, sa_column=Column("gi_synonyms", String))
    db_xrefs: str | None = Field(default=None, sa_column=Column("gi_dbxrefs", String))
    chromosome: str | None = Field(default=None, sa_column=Column("gi_chrom", String(255)))
    map_location: str | None = Field(default=None, sa_column=Column("gi_map_location", String))
    description: str | None = Field(default=None, sa_column=Column("gi_description", Text))
    type_of_gene: str | None = Field(default=None, sa_column=Column("gi_type_of_gene", String))
    symbol_from_nomenclature_authority: str | None = Field(
        default=None, sa_column=Column("gi_sym_from_nome_auth", String)
    )
    full_name_from_nomenclature_authority: str | None = Field(
        default=None, sa_column=Column("gi_full_name_from_nome_auth", String)
    )
    nomenclature_status: str | None = Field(default=None, sa_column=Column("gi_nome_status", String))
    other_designations: str | None = Field(default=None, sa_column=Column("gi_other_designations", String))
    modification_date: str | None = Field(default=None, sa_column=Column("gi_modification_date", String))
    hgnc_id: int | None = Field(default=None, sa_column=Column("gi_hgnc_id", Integer))
