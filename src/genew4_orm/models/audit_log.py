"""AuditLog model for tracking database write operations.

This model stores audit trail information for all CREATE, UPDATE,
and DELETE operations on database entities.
"""

import json
from datetime import datetime
from typing import Any

from db_common import DeclarativeBase
from sqlalchemy import DateTime, Integer, String, Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column


def _serialize_field_changes(value: dict[str, Any] | None) -> str | None:
    """Serialize field changes dict to JSON string for database storage."""
    if value is None:
        return None
    return json.dumps(value)


def _deserialize_field_changes(value: str | None) -> dict[str, Any]:
    """Deserialize field changes JSON string from database storage."""
    if value is None:
        return {}
    return json.loads(value)  # type: ignore[no-any-return]


class JSONEncodedDict(TypeDecorator[dict[str, Any]]):
    """Store a Python ``dict`` in a ``TEXT`` column, serialized as JSON.

    Implements the JSON-in-TEXT ``TypeDecorator`` pattern from the SQLAlchemy
    docs: ``process_bind_param`` serializes a dict to a JSON string on write and
    ``process_result_value`` deserializes it back to a dict on read. This makes
    ``AuditLog.field_changes`` honor its ``Mapped[dict[str, Any]]`` annotation
    across a database round-trip (previously the column was plain ``Text``, so a
    dict could not be persisted and a loaded row came back as a JSON string,
    breaking ``get_field_diff`` / ``get_changed_fields``).

    The column DDL remains ``TEXT`` (``impl = Text``), so this is a Python-side
    (de)serialization change with no schema migration.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: dict[str, Any] | None, dialect: Any) -> str | None:
        """Serialize dict -> JSON string for the database."""
        return _serialize_field_changes(value)

    def process_result_value(self, value: str | None, dialect: Any) -> dict[str, Any]:
        """Deserialize JSON string -> dict from the database."""
        return _deserialize_field_changes(value)


class AuditLog(DeclarativeBase):
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

    id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Primary key",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True, comment="When the operation occurred"
    )
    user: Mapped[str] = mapped_column(String(100), nullable=False, comment="User who performed the operation")
    operation: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="Operation type: CREATE, UPDATE, or DELETE"
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, comment="Type of entity affected")
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="ID of the affected entity")
    field_changes: Mapped[dict[str, Any]] = mapped_column(
        "field_changes",
        JSONEncodedDict,
        nullable=False,
        default={},
        comment="JSON dict with old/new values for changed fields (stored as Text)",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize an AuditLog, applying SQLModel-parity instantiation defaults.

        Plain SQLAlchemy 2.0 only applies ``mapped_column(default=...)`` at flush,
        not construction. ``timestamp`` defaults to ``datetime.utcnow()`` and
        ``field_changes`` defaults to a fresh ``{}`` at instantiation (as SQLModel
        did), unless explicitly provided.
        """
        if "timestamp" not in kwargs:
            self.timestamp = datetime.utcnow()
        if "field_changes" not in kwargs:
            self.field_changes = {}
        super().__init__(**kwargs)

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
