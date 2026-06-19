"""Correspondence model representing the corr table.

This model contains correspondence record information.
"""

from db_common import DeclarativeBase
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column


class Correspondence(DeclarativeBase):
    """Correspondence entity representing the corr table.

    Records of correspondence with researchers and organizations.
    """

    __tablename__ = "corr"

    # Region: Editing
    lock: Mapped[str | None] = mapped_column("corr_lock", Text, comment="Lock flag for editing")

    # Region: Core fields
    id: Mapped[int | None] = mapped_column(
        "corr_id",
        primary_key=True, nullable=False,
        comment="Primary key",
    )
    first_name: Mapped[str | None] = mapped_column("corr_first_name", Text, comment="Contact first name")
    last_name: Mapped[str | None] = mapped_column("corr_last_name", Text, comment="Contact last name")
    email: Mapped[str | None] = mapped_column("corr_email", Text, comment="Contact email address")
    notes: Mapped[str | None] = mapped_column("corr_notes", Text, comment="Correspondence notes")
    address: Mapped[str | None] = mapped_column("corr_address", Text, comment="Contact address")
    date_received: Mapped[str | None] = mapped_column("corr_date_recev", Text, comment="Date correspondence received")
    date_sent: Mapped[str | None] = mapped_column("corr_date_sent", Text, comment="Date correspondence sent")
    # These emails can be large data, only query if needed
    email_received: Mapped[str | None] = mapped_column("corr_recev_email", Text, comment="Received email content")
    email_sent: Mapped[str | None] = mapped_column("corr_sent_email", Text, comment="Sent email content")

    # Note: Many-to-many with GeneGroup is through FamHasCorr junction table
    # Query via: session.scalars(select(Correspondence).join(FamHasCorr).join(GeneGroup)).all()

    def __repr__(self) -> str:
        """Return string representation of Correspondence."""
        return f"<Correspondence(id={self.id}, email='{self.email}')>"
