"""Gene2Refseq model for the gene2refseq table.

Used by coord-builder (NCBI sub-source) and xref-loader (gene2refseq loader).
Staging columns are all varchar per the Perl source; production types may differ.
"""

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class Gene2Refseq(SQLModel, table=True):
    """NCBI Gene-to-RefSeq mapping record.

    Stores the mapping between NCBI Entrez Gene IDs and RefSeq accessions,
    including genomic coordinates and assembly information.

    Composite primary key: (g2r_tax_id, g2r_eg_id, g2r_rna_nt_acc_ver).
    The PK field names match their column names so that SQLModel's
    Field(primary_key=True) mechanism works alongside sa_column fields.
    """

    __tablename__ = "gene2refseq"

    g2r_tax_id: str | None = Field(default=None, primary_key=True)
    g2r_eg_id: str | None = Field(default=None, primary_key=True)
    status: str | None = Field(default=None, sa_column=Column("g2r_status", String))
    g2r_rna_nt_acc_ver: str | None = Field(default=None, primary_key=True)
    rna_nt_gi: str | None = Field(default=None, sa_column=Column("g2r_rna_nt_gi", String))
    prot_acc_ver: str | None = Field(default=None, sa_column=Column("g2r_prot_acc_ver", String))
    prot_gi: str | None = Field(default=None, sa_column=Column("g2r_prot_gi", String))
    gen_nt_acc_ver: str | None = Field(default=None, sa_column=Column("g2r_gen_nt_acc_ver", String))
    gen_nt_gi: str | None = Field(default=None, sa_column=Column("g2r_gen_nt_gi", String))
    start_pos_gen_acc: str | None = Field(default=None, sa_column=Column("g2r_start_pos_gen_acc", String))
    end_pos_gen_acc: str | None = Field(default=None, sa_column=Column("g2r_end_pos_gen_acc", String))
    orientation: str | None = Field(default=None, sa_column=Column("g2r_orientation", String))
    assembly: str | None = Field(default=None, sa_column=Column("g2r_assembly", String))
    mat_pept_acc_ver: str | None = Field(default=None, sa_column=Column("g2r_mat_pept_acc_ver", String))
    mat_pept_gi: str | None = Field(default=None, sa_column=Column("g2r_mat_pept_gi", String))
    symbol: str | None = Field(default=None, sa_column=Column("g2r_symbol", String))
