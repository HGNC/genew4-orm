"""Gene model representing the hgnc table.

This model contains all 40+ fields from hgnc table matching
TypeScript ORM implementation in hgnc-tools-api.
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, Integer, String, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene_has_comment import GeneHasComment
    from genew4_orm.models.gene_has_gene_group import GeneHasGeneGroup


class Gene(SQLModel, table=True):
    """Gene entity representing hgnc table.

    Contains comprehensive gene information including symbols, names,
    locus type, status, external references, dates, and relationships
    to gene groups.
    """

    __tablename__ = "hgnc"

    # Region: Editing
    lock: str | None = Field(default=None, sa_column=Column("hgnc_lock", Text))

    # Region: Core Public Data Fields
    hgnc_id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key: HGNC ID",
    )
    approved_symbol: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_app_sym", String(255)),
        description="Approved gene symbol",
    )
    approved_name: str | None = Field(
        default=None,
        sa_column=Column("hgnc_app_name", Text),
        description="Approved gene name",
    )
    # Note: Database column is hgnc_locus_type (not locus_type), using VARCHAR with no enum
    locus_type: str | None = Field(
        default="undef",
        sa_column=Column("hgnc_locus_type", String(255)),
        description="Gene locus type classification",
    )
    status: str | None = Field(
        default="Pending",
        sa_column=Column("hgnc_status", String(255)),
        description="Gene approval status",
    )
    previous_symbols: str | None = Field(
        default=None,
        sa_column=Column("hgnc_prev_sym", Text),
        description="Previous gene symbols",
    )
    previous_names: str | None = Field(
        default=None,
        sa_column=Column("hgnc_prev_name", Text),
        description="Previous gene names",
    )
    alias_symbols: str | None = Field(
        default=None,
        sa_column=Column("hgnc_aliases", Text),
        description="Alias gene symbols",
    )
    alias_names: str | None = Field(
        default=None,
        sa_column=Column("hgnc_other_names", Text),
        description="Alias gene names",
    )
    chromosomal_location: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_pub_chrom_map", String(255)),
        description="Public chromosomal mapping",
    )

    # Region: Core Internal Data Fields
    editor: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_editor", String(255)),
        description="Editor responsible",
    )
    priority: str | None = Field(
        default=None,
        sa_column=Column("hgnc_priority", Text),
        description="Gene priority",
    )
    correspondence_ids: str | None = Field(
        default=None,
        sa_column=Column("hgnc_corr_ids", Text),
        description="Correspondence IDs",
    )
    additional_info: str | None = Field(
        default=None,
        sa_column=Column("hgnc_add_info", Text),
        description="Additional information",
    )
    edit_memo: str | None = Field(
        default=None,
        sa_column=Column("hgnc_edit_memo", Text),
        description="Edit memo",
    )
    reserved_symbols: str | None = Field(
        default=None,
        sa_column=Column("hgnc_res_sym", Text),
        description="Reserved symbols",
    )
    reserved_names: str | None = Field(
        default=None,
        sa_column=Column("hgnc_res_name", Text),
        description="Reserved names",
    )
    reserved_alias_symbols: str | None = Field(
        default=None,
        sa_column=Column("hgnc_res_alias", Text),
        description="Reserved alias symbols",
    )

    # Region: External References
    public_ncbi_gene_id: int | None = Field(
        default=None,
        sa_column=Column("hgnc_pub_eg_id", Integer),
        description="Public NCBI Gene ID (Entrez Gene)",
    )
    ncbi_gene_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_eg_ids", String(255)),
        description="NCBI Gene IDs",
    )
    public_refseq_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_pub_refseq_ids", Text),
        description="Public RefSeq IDs",
    )
    public_ensembl_id: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_pub_ensembl_id", Text),
        description="Public Ensembl ID",
    )
    mgd_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_mgd_id", Text),
        description="Mouse Genome Database IDs",
    )
    public_pubmed_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_pub_pubmed_ids", String(255)),
        description="Public PubMed IDs",
    )
    pubmed_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_pubmed_ids", Text),
        description="PubMed IDs",
    )
    enzyme_commission_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_enz_ids", String(255)),
        description="Enzyme Commission IDs",
    )
    specialist_resources: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_other_ids", Text),
        description="Specialist resource IDs",
    )
    public_insd_c_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_pub_acc_ids", String(255)),
        description="Public INSDC IDs",
    )
    insdc_ids: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("hgnc_acc_ids", Text),
        description="International Nucleotide Sequence Database Collaboration IDs",
    )

    # Region: Date-Related Fields
    date_submitted: date | None = Field(
        default=None,
        sa_column=Column("hgnc_date_sub", Date),
        description="Date submitted",
    )
    date_to_approve_or_reserve: date | None = Field(
        default=None,
        sa_column=Column("hgnc_date2app_or_res", Date),
        description="Date to approve or reserve",
    )
    date_modified: date | None = Field(
        default=None,
        sa_column=Column("hgnc_date_mod", Date),
        description="Date modified",
    )
    date_symbol_changed: date | None = Field(
        default=None,
        sa_column=Column("hgnc_date_sym_change", Date),
        description="Date symbol changed",
    )
    date_name_changed: date | None = Field(
        default=None,
        sa_column=Column("hgnc_date_name_change", Date),
        description="Date name changed",
    )
    date_stable_symbol_changed: date | None = Field(
        default=None,
        sa_column=Column("hgnc_date_stable_symbol_change", Date),
        description="Date stable symbol changed",
    )

    # Region: Stabilisation Fields
    ambiguous: bool | None = Field(
        default=None,
        sa_column=Column("hgnc_ambiguous", Boolean),
        description="Ambiguous flag",
    )
    to_review: bool | None = Field(
        default=None,
        sa_column=Column("hgnc_to_review", Boolean),
        description="To review flag",
    )
    tgmi_stable_symbol: bool | None = Field(
        default=None,
        sa_column=Column("hgnc_tgmi_stable_symbol", Boolean),
        description="TGMI stable symbol flag",
    )

    # Region: Relationships
    gene_has_gene_groups: list["GeneHasGeneGroup"] = Relationship(
        back_populates="gene",
        cascade_delete=True,
    )
    gene_has_comments: list["GeneHasComment"] = Relationship(
        back_populates="gene",
        cascade_delete=True,
    )

    def __repr__(self) -> str:
        """Return string representation of Gene."""
        return f"<Gene(hgnc_id={self.hgnc_id}, approved_symbol='{self.approved_symbol}')>"
