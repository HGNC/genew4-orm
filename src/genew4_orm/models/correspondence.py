"""Correspondence model representing the corr table.

This model contains correspondence record information.
"""


from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Correspondence(SQLModel, table=True):
    """Correspondence entity representing the corr table.

    Records of correspondence with researchers and organizations.
    """

    __tablename__ = "corr"

    # Region: Editing
    lock: str | None = Field(
        default=None,
        sa_column=Column("corr_lock", Text),
        description="Lock flag for editing",
    )

    # Region: Core fields
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "corr_id"},
        description="Primary key",
    )
    first_name: str | None = Field(
        default=None,
        sa_column=Column("corr_first_name", Text),
        description="Contact first name",
    )
    last_name: str | None = Field(
        default=None,
        sa_column=Column("corr_last_name", Text),
        description="Contact last name",
    )
    email: str | None = Field(
        default=None,
        sa_column=Column("corr_email", Text),
        description="Contact email address",
    )
    notes: str | None = Field(
        default=None,
        sa_column=Column("corr_notes", Text),
        description="Correspondence notes",
    )
    address: str | None = Field(
        default=None,
        sa_column=Column("corr_address", Text),
        description="Contact address",
    )
    date_received: str | None = Field(
        default=None,
        sa_column=Column("corr_date_recev", Text),
        description="Date correspondence received",
    )
    date_sent: str | None = Field(
        default=None,
        sa_column=Column("corr_date_sent", Text),
        description="Date correspondence sent",
    )
    # These emails can be large data, only query if needed
    email_received: str | None = Field(
        default=None,
        sa_column=Column("corr_recev_email", Text),
        description="Received email content",
    )
    email_sent: str | None = Field(
        default=None,
        sa_column=Column("corr_sent_email", Text),
        description="Sent email content",
    )

    # Note: Many-to-many with GeneGroup is through FamHasCorr junction table
    # Query via: session.query(Correspondence).join(FamHasCorr).join(GeneGroup)

    def __repr__(self) -> str:
        """Return string representation of Correspondence."""
        return f"<Correspondence(id={self.id}, email='{self.email}')>"
