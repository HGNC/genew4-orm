"""Gene2Refseq model for the gene2refseq table.

Used by coord-builder (NCBI sub-source) and xref-loader (gene2refseq loader).
Staging columns are all varchar per the Perl source; production types may differ.
"""

from db_common import DeclarativeBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Gene2Refseq(DeclarativeBase):
    """NCBI Gene-to-RefSeq mapping record.

    Stores the mapping between NCBI Entrez Gene IDs and RefSeq accessions,
    including genomic coordinates and assembly information.

    Composite primary key: (g2r_tax_id, g2r_eg_id, g2r_rna_nt_acc_ver).
    The PK field names match their column names so that ``mapped_column(primary_key=True, nullable=False)``
    works alongside the other ``mapped_column("...", String)`` fields.
    """

    __tablename__ = "gene2refseq"

    g2r_tax_id: Mapped[str | None] = mapped_column(primary_key=True, nullable=False)
    g2r_eg_id: Mapped[str | None] = mapped_column(primary_key=True, nullable=False)
    status: Mapped[str | None] = mapped_column("g2r_status", String)
    g2r_rna_nt_acc_ver: Mapped[str | None] = mapped_column(primary_key=True, nullable=False)
    rna_nt_gi: Mapped[str | None] = mapped_column("g2r_rna_nt_gi", String)
    prot_acc_ver: Mapped[str | None] = mapped_column("g2r_prot_acc_ver", String)
    prot_gi: Mapped[str | None] = mapped_column("g2r_prot_gi", String)
    gen_nt_acc_ver: Mapped[str | None] = mapped_column("g2r_gen_nt_acc_ver", String)
    gen_nt_gi: Mapped[str | None] = mapped_column("g2r_gen_nt_gi", String)
    start_pos_gen_acc: Mapped[str | None] = mapped_column("g2r_start_pos_gen_acc", String)
    end_pos_gen_acc: Mapped[str | None] = mapped_column("g2r_end_pos_gen_acc", String)
    orientation: Mapped[str | None] = mapped_column("g2r_orientation", String)
    assembly: Mapped[str | None] = mapped_column("g2r_assembly", String)
    mat_pept_acc_ver: Mapped[str | None] = mapped_column("g2r_mat_pept_acc_ver", String)
    mat_pept_gi: Mapped[str | None] = mapped_column("g2r_mat_pept_gi", String)
    symbol: Mapped[str | None] = mapped_column("g2r_symbol", String)
