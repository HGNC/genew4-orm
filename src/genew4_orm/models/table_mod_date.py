"""TableModDate model for version staleness checks.

Maps to the table_mod_dates table used by all Phase 2 loaders
to track which data source version was last loaded.
"""

from datetime import datetime

from db_common import DeclarativeBase
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class TableModDate(DeclarativeBase):
    """Version tracking record for genew4 tables.

    Tracks the last modification date and version string for each
    tracked table, enabling incremental load decisions.
    """

    __tablename__ = "table_mod_dates"

    table_name: Mapped[str | None] = mapped_column(
        String(100),
        primary_key=True, nullable=False,
        comment="Target table name (primary key)",
    )
    version: Mapped[str | None] = mapped_column("version", String(255), comment="Last-loaded source version string")
    version_type: Mapped[str | None] = mapped_column(
        "version_type", String(100), comment="Optional version type classification"
    )
    mod_date: Mapped[datetime | None] = mapped_column("mod_date", DateTime, comment="Timestamp of last modification")
