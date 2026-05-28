"""HgncId2CcdsId model for the hgnc_id2ccds_id junction table.

Used by xref-loader (CCDS post-load) to maintain the many-to-many
relationship between HGNC IDs and CCDS identifiers.
"""

from sqlmodel import Field, SQLModel


class HgncId2CcdsId(SQLModel, table=True):
    """Mapping between HGNC IDs and CCDS identifiers.

    Junction table linking HGNC gene identifiers to their corresponding
    CCDS (Consensus Coding Sequence) identifiers.
    """

    __tablename__ = "hgnc_id2ccds_id"

    hgnc_id2ccds_id_hgnc_id: int | None = Field(
        default=None,
        primary_key=True,
        description="HGNC ID (composite primary key)",
    )
    hgnc_id2ccds_id_ccds_id: str | None = Field(
        default=None,
        primary_key=True,
        max_length=50,
        description="CCDS identifier (composite primary key)",
    )
