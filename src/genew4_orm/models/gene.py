"""Gene model representing the hgnc table.

This model contains all 40+ fields from hgnc table matching
TypeScript ORM implementation in hgnc-tools-api.
"""

from datetime import date
from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.gene_has_comment import GeneHasComment
    from genew4_orm.models.gene_has_gene_group import GeneHasGeneGroup


class Gene(DeclarativeBase):
    """Gene entity representing hgnc table.

    Contains comprehensive gene information including symbols, names,
    locus type, status, external references, dates, and relationships
    to gene groups.
    """

    __tablename__ = "hgnc"

    # Region: Editing
    lock: Mapped[str | None] = mapped_column("hgnc_lock", Text)

    # Region: Core Public Data Fields
    hgnc_id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Primary key: HGNC ID",
    )
    approved_symbol: Mapped[str | None] = mapped_column("hgnc_app_sym", String(255), comment="Approved gene symbol")
    approved_name: Mapped[str | None] = mapped_column("hgnc_app_name", Text, comment="Approved gene name")
    # Note: Database column is hgnc_locus_type (not locus_type), using VARCHAR with no enum
    locus_type: Mapped[str | None] = mapped_column(
        "hgnc_locus_type", String(255), default="undef", comment="Gene locus type classification"
    )
    status: Mapped[str | None] = mapped_column(
        "hgnc_status", String(255), default="Pending", comment="Gene approval status"
    )
    previous_symbols: Mapped[str | None] = mapped_column("hgnc_prev_sym", Text, comment="Previous gene symbols")
    previous_names: Mapped[str | None] = mapped_column("hgnc_prev_name", Text, comment="Previous gene names")
    alias_symbols: Mapped[str | None] = mapped_column("hgnc_aliases", Text, comment="Alias gene symbols")
    alias_names: Mapped[str | None] = mapped_column("hgnc_other_names", Text, comment="Alias gene names")
    chromosomal_location: Mapped[str | None] = mapped_column(
        "hgnc_pub_chrom_map", String(255), comment="Public chromosomal mapping"
    )

    # Region: Core Internal Data Fields
    editor: Mapped[str | None] = mapped_column("hgnc_editor", String(255), comment="Editor responsible")
    priority: Mapped[str | None] = mapped_column("hgnc_priority", Text, comment="Gene priority")
    correspondence_ids: Mapped[str | None] = mapped_column("hgnc_corr_ids", Text, comment="Correspondence IDs")
    additional_info: Mapped[str | None] = mapped_column("hgnc_add_info", Text, comment="Additional information")
    edit_memo: Mapped[str | None] = mapped_column("hgnc_edit_memo", Text, comment="Edit memo")
    reserved_symbols: Mapped[str | None] = mapped_column("hgnc_res_sym", Text, comment="Reserved symbols")
    reserved_names: Mapped[str | None] = mapped_column("hgnc_res_name", Text, comment="Reserved names")
    reserved_alias_symbols: Mapped[str | None] = mapped_column("hgnc_res_alias", Text, comment="Reserved alias symbols")

    # Region: External References
    public_ncbi_gene_id: Mapped[int | None] = mapped_column(
        "hgnc_pub_eg_id", Integer, comment="Public NCBI Gene ID (Entrez Gene)"
    )
    ncbi_gene_ids: Mapped[str | None] = mapped_column("hgnc_eg_ids", String(255), comment="NCBI Gene IDs")
    public_refseq_ids: Mapped[str | None] = mapped_column("hgnc_pub_refseq_ids", Text, comment="Public RefSeq IDs")
    public_ensembl_id: Mapped[str | None] = mapped_column("hgnc_pub_ensembl_id", Text, comment="Public Ensembl ID")
    mgd_ids: Mapped[str | None] = mapped_column("hgnc_mgd_id", Text, comment="Mouse Genome Database IDs")
    public_pubmed_ids: Mapped[str | None] = mapped_column(
        "hgnc_pub_pubmed_ids", String(255), comment="Public PubMed IDs"
    )
    pubmed_ids: Mapped[str | None] = mapped_column("hgnc_pubmed_ids", Text, comment="PubMed IDs")
    enzyme_commission_ids: Mapped[str | None] = mapped_column(
        "hgnc_enz_ids", String(255), comment="Enzyme Commission IDs"
    )
    specialist_resources: Mapped[str | None] = mapped_column("hgnc_other_ids", Text, comment="Specialist resource IDs")
    public_insd_c_ids: Mapped[str | None] = mapped_column("hgnc_pub_acc_ids", String(255), comment="Public INSDC IDs")
    insdc_ids: Mapped[str | None] = mapped_column(
        "hgnc_acc_ids", Text, comment="International Nucleotide Sequence Database Collaboration IDs"
    )

    # Region: Date-Related Fields
    date_submitted: Mapped[date | None] = mapped_column("hgnc_date_sub", Date, comment="Date submitted")
    date_to_approve_or_reserve: Mapped[date | None] = mapped_column(
        "hgnc_date2app_or_res", Date, comment="Date to approve or reserve"
    )
    date_modified: Mapped[date | None] = mapped_column("hgnc_date_mod", Date, comment="Date modified")
    date_symbol_changed: Mapped[date | None] = mapped_column(
        "hgnc_date_sym_change", Date, comment="Date symbol changed"
    )
    date_name_changed: Mapped[date | None] = mapped_column("hgnc_date_name_change", Date, comment="Date name changed")
    date_stable_symbol_changed: Mapped[date | None] = mapped_column(
        "hgnc_date_stable_symbol_change", Date, comment="Date stable symbol changed"
    )

    # Region: Stabilisation Fields
    ambiguous: Mapped[bool | None] = mapped_column("hgnc_ambiguous", Boolean, comment="Ambiguous flag")
    to_review: Mapped[bool | None] = mapped_column("hgnc_to_review", Boolean, comment="To review flag")
    tgmi_stable_symbol: Mapped[bool | None] = mapped_column(
        "hgnc_tgmi_stable_symbol", Boolean, comment="TGMI stable symbol flag"
    )

    # Region: Phase 2 Cross-Reference and Sequence Fields
    ccds_ids: Mapped[str | None] = mapped_column(
        "hgnc_ccds_ids", Text, comment="Comma-separated CCDS IDs associated with this gene"
    )
    hseq_ids: Mapped[str | None] = mapped_column(
        "hgnc_hseq_ids", Text, comment="Comma-separated HSeq IDs associated with this gene"
    )
    public_hseq_id: Mapped[str | None] = mapped_column("hgnc_pub_hseq_id", Text, comment="Public HSeq ID for this gene")
    pseudogene_id: Mapped[int | None] = mapped_column(
        "hgnc_pseudogene_id", Integer, comment="Pseudogene.org ID linked to this gene"
    )
    vega_ids: Mapped[str | None] = mapped_column(
        "hgnc_vega_ids", Text, comment="Vega (Otter) gene IDs associated with this gene"
    )

    # Region: Relationships
    gene_has_gene_groups: Mapped[list["GeneHasGeneGroup"]] = relationship(
        back_populates="gene",
        cascade="all, delete-orphan",
    )
    gene_has_comments: Mapped[list["GeneHasComment"]] = relationship(
        back_populates="gene",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of Gene."""
        return f"<Gene(hgnc_id={self.hgnc_id}, approved_symbol='{self.approved_symbol}')>"
