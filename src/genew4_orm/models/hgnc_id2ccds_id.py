"""HgncId2CcdsId model for the hgnc_id2ccds_id junction table.

Used by xref-loader (CCDS post-load) to maintain the many-to-many
relationship between HGNC IDs and CCDS identifiers.
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class HgncId2CcdsId(DeclarativeBase):
    """Mapping between HGNC IDs and CCDS identifiers.

    Junction table linking HGNC gene identifiers to their corresponding
    CCDS (Consensus Coding Sequence) identifiers.
    """

    __tablename__ = "hgnc_id2ccds_id"

    hgnc_id2ccds_id_hgnc_id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="HGNC ID (composite primary key)",
    )
    hgnc_id2ccds_id_ccds_id: Mapped[str | None] = mapped_column(
        String(50),
        primary_key=True,
        nullable=False,
        comment="CCDS identifier (composite primary key)",
    )
