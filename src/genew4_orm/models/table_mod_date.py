"""TableModDate model for version staleness checks.

Maps to the table_mod_dates table used by all Phase 2 loaders
to track which data source version was last loaded.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel


class TableModDate(SQLModel, table=True):
    """Version tracking record for genew4 tables.

    Tracks the last modification date and version string for each
    tracked table, enabling incremental load decisions.
    """

    __tablename__ = "table_mod_dates"

    table_name: str | None = Field(
        default=None,
        primary_key=True,
        max_length=100,
        description="Target table name (primary key)",
    )
    version: str | None = Field(
        default=None,
        sa_column=Column("version", String(255)),
        description="Last-loaded source version string",
    )
    version_type: str | None = Field(
        default=None,
        sa_column=Column("version_type", String(100)),
        description="Optional version type classification",
    )
    mod_date: datetime | None = Field(
        default=None,
        sa_column=Column("mod_date", DateTime),
        description="Timestamp of last modification",
    )
