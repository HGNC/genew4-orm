"""AuditLog model for tracking database write operations.

This model stores audit trail information for all CREATE, UPDATE,
and DELETE operations on database entities.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlmodel import Field, SQLModel
import json


def _serialize_field_changes(value: dict[str, Any] | None) -> str | None:
    """Serialize field changes dict to JSON string for database storage."""
    if value is None:
        return None
    return json.dumps(value)


def _deserialize_field_changes(value: str | None) -> dict[str, Any]:
    """Deserialize field changes JSON string from database storage."""
    if value is None:
        return {}
    return json.loads(value)


class AuditLog(SQLModel, table=True):
    """Audit log entry for tracking write operations.

    Records all CREATE, UPDATE, and DELETE operations with field-level
    change tracking. Used for compliance, debugging, and data history.

    Attributes:
        id: Primary key.
        timestamp: When the operation occurred.
        user: User who performed the operation.
        operation: Type of operation (CREATE, UPDATE, DELETE).
        entity_type: Type of entity affected (e.g., "Gene", "GeneGroup").
        entity_id: ID of the affected entity.
        field_changes: JSON dict with old/new values for changed fields.
    """

    __tablename__ = "audit_log"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, default=datetime.utcnow),
        description="When the operation occurred",
    )
    user: str = Field(
        max_length=100,
        sa_column=Column(String(100), nullable=False),
        description="User who performed the operation",
    )
    operation: str = Field(
        max_length=10,
        sa_column=Column(String(10), nullable=False),
        description="Operation type: CREATE, UPDATE, or DELETE",
    )
    entity_type: str = Field(
        max_length=100,
        sa_column=Column(String(100), nullable=False),
        description="Type of entity affected",
    )
    entity_id: int = Field(
        sa_column=Column(Integer, nullable=False),
        description="ID of the affected entity",
    )
    field_changes: dict[str, Any] = Field(
        default={},
        sa_column=Column(
            "field_changes",
            Text,
            nullable=False,
        ),
        description="JSON dict with old/new values for changed fields (stored as Text)",
    )

    def __repr__(self) -> str:
        """Return string representation of AuditLog."""
        return (
            f"<AuditLog(id={self.id}, operation={self.operation}, "
            f"entity_type={self.entity_type}, entity_id={self.entity_id})>"
        )

    def get_field_diff(self, field_name: str) -> dict[str, Any] | None:
        """Get the old/new values for a specific field.

        Args:
            field_name: Name of the field to get diff for.

        Returns:
            Dict with 'old' and 'new' keys, or None if field not in changes.
        """
        return self.field_changes.get(field_name)

    def get_changed_fields(self) -> list[str]:
        """Get list of field names that were changed.

        Returns:
            List of field names that have changes recorded.
        """
        return list(self.field_changes.keys())
