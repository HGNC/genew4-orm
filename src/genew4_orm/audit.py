"""Audit logging system for tracking database write operations.

This module provides automatic audit logging for all CREATE, UPDATE,
and DELETE operations using SQLAlchemy event listeners.
"""

import json
from typing import Any

from sqlalchemy import event, desc
from sqlalchemy.orm import Session

from genew4_orm.models.audit_log import AuditLog

# Fields to exclude from audit logging (sensitive or large data)
EXCLUDED_FIELDS = {
    "password",
    "jwt_token",
    "refresh_token",
    "access_token",
    "secret",
    "api_key",
    "email_body",
    "email_html",
    "large_text",
}

# Fields that should always be logged despite exclusion rules
ALWAYS_LOG_FIELDS = {
    "id",
    "approved_symbol",
    "name",
    "status",
}


def should_log_field(field_name: str, value: Any) -> bool:
    """Determine if a field should be included in audit logging.

    Args:
        field_name: Name of the field to check.
        value: Value of the field.

    Returns:
        True if the field should be logged, False otherwise.
    """
    # Always log certain fields
    if field_name in ALWAYS_LOG_FIELDS:
        return True

    # Exclude sensitive fields
    if field_name in EXCLUDED_FIELDS:
        return False

    # Exclude fields with sensitive keywords
    field_lower = field_name.lower()
    for excluded in EXCLUDED_FIELDS:
        if excluded in field_lower:
            return False

    # Exclude large text values
    if value is not None and isinstance(value, str | bytes):
        if len(value) > 10000:  # 10KB threshold
            return False

    return True


def is_json_serializable(value: Any) -> bool:
    """Check if a value can be JSON serialized.

    Args:
        value: Value to check.

    Returns:
        True if value is JSON serializable, False otherwise.
    """
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def get_field_changes(
    instance: Any,
    operation: str,
) -> dict[str, dict[str, Any]]:
    """Get field changes for an instance.

    Args:
        instance: The SQLAlchemy model instance.
        operation: Operation type ('INSERT', 'UPDATE', 'DELETE').

    Returns:
        Dict mapping field names to {'old': value, 'new': value} dicts.
        For INSERT, old values are None.
        For DELETE, new values are None.
    """
    changes: dict[str, dict[str, Any]] = {}

    if operation == "INSERT":
        # For new objects, log all non-internal fields
        state = instance.__dict__
        for key, value in state.items():
            if not key.startswith("_") and should_log_field(key, value):
                # Only log if value is JSON serializable
                if is_json_serializable(value):
                    changes[key] = {"old": None, "new": value}

    elif operation == "DELETE":
        # For deleted objects, log all non-internal fields
        state = instance.__dict__
        for key, value in state.items():
            if not key.startswith("_") and should_log_field(key, value):
                # Only log if value is JSON serializable
                if is_json_serializable(value):
                    changes[key] = {"old": value, "new": None}

    elif operation == "UPDATE":
        # For updates, only log changed fields
        state = instance.__dict__
        for key in state.keys():
            if key.startswith("_"):
                continue

            # Get the history of this attribute
            if hasattr(instance, "_sa_instance_state"):
                attrs = instance._sa_instance_state.attrs
                if key in attrs:
                    attr_history = attrs[key].history
                    if attr_history.has_changes():
                        old_value = attr_history.deleted[0] if attr_history.deleted else None
                        new_value = attr_history.added[0] if attr_history.added else None

                        if should_log_field(key, new_value):
                            # Only log if values are JSON serializable
                            if is_json_serializable(old_value) and is_json_serializable(new_value):
                                changes[key] = {"old": old_value, "new": new_value}

    return changes


def get_entity_info(instance: Any) -> tuple[str, int]:
    """Extract entity type and ID from an instance.

    Args:
        instance: The SQLAlchemy model instance.

    Returns:
        Tuple of (entity_type_name, entity_id).
    """
    entity_type = instance.__class__.__name__
    # Try common primary key attribute names
    entity_id = (
        getattr(instance, "id", None)
        or getattr(instance, "hgnc_id", None)
        or getattr(instance, "family_new_id", None)
        or 0
    )
    return entity_type, entity_id


@event.listens_for(Session, "before_flush")
def audit_write_operations(
    session: Session,
    context: Any = None,
    instances: list[Any] | None = None,
) -> None:
    """Audit write operations (INSERT, UPDATE, DELETE) before session flush.

    This event listener captures all write operations and creates AuditLog
    entries. The audit log entries are added to the same session, ensuring
    transactional atomicity.

    Note: For INSERT operations, the entity_id will be 0 since the ID
    isn't assigned yet. Query audit logs by other fields (entity_type, user, etc.)
    or use the field_changes JSON to identify the specific entity.

    Args:
        session: The SQLAlchemy session being flushed.
        context: The flush context - passed first to match SQLAlchemy event signature.
        instances: Optional list of instances being flushed (unused).
    """
    # Skip audit logging for read-only sessions
    if session.info.get("read_only", False):
        return

    # Get user from session info (should be set by get_readwrite_session)
    user = session.info.get("user", "unknown")

    # Track objects we've already audited to avoid duplicates
    audited_instances: set[int] = set()

    # Process new instances (INSERT)
    for instance in session.new:
        if id(instance) in audited_instances:
            continue

        entity_type, entity_id = get_entity_info(instance)
        field_changes = get_field_changes(instance, "INSERT")

        if field_changes:  # Only log if there are fields to log
            audit_entry = AuditLog(
                user=user,
                operation="CREATE",
                entity_type=entity_type,
                entity_id=entity_id,  # Will be 0 for new entities
                field_changes=json.dumps(field_changes),
            )
            session.add(audit_entry)
            audited_instances.add(id(instance))

    # Process dirty instances (UPDATE)
    for instance in session.dirty:
        if id(instance) in audited_instances:
            continue

        entity_type, entity_id = get_entity_info(instance)
        field_changes = get_field_changes(instance, "UPDATE")

        if field_changes:  # Only log if there are actual changes
            audit_entry = AuditLog(
                user=user,
                operation="UPDATE",
                entity_type=entity_type,
                entity_id=entity_id,
                field_changes=json.dumps(field_changes),
            )
            session.add(audit_entry)
            audited_instances.add(id(instance))

    # Process deleted instances (DELETE)
    for instance in session.deleted:
        if id(instance) in audited_instances:
            continue

        entity_type, entity_id = get_entity_info(instance)
        field_changes = get_field_changes(instance, "DELETE")

        if field_changes:  # Only log if there are fields to log
            audit_entry = AuditLog(
                user=user,
                operation="DELETE",
                entity_type=entity_type,
                entity_id=entity_id,
                field_changes=json.dumps(field_changes),
            )
            session.add(audit_entry)
            audited_instances.add(id(instance))


def get_audit_entries_for_entity(
    session: Session,
    entity_type: str,
    entity_id: int,
    limit: int = 100,
) -> list[AuditLog]:
    """Get audit log entries for a specific entity.

    Args:
        session: The SQLAlchemy session.
        entity_type: Type of entity to query.
        entity_id: ID of the entity to query.
        limit: Maximum number of entries to return.

    Returns:
        List of AuditLog entries, ordered by most recent first.
    """
    return (
        session.query(AuditLog)
        .filter(AuditLog.entity_type == entity_type)  # type: ignore[arg-type]
        .filter(AuditLog.entity_id == entity_id)  # type: ignore[arg-type]
        .order_by(desc(AuditLog.timestamp))  # type: ignore[arg-type]
        .limit(limit)
        .all()
    )


def get_user_audit_history(
    session: Session,
    user: str,
    limit: int = 100,
) -> list[AuditLog]:
    """Get audit log entries for a specific user.

    Args:
        session: The SQLAlchemy session.
        user: Username to query.
        limit: Maximum number of entries to return.

    Returns:
        List of AuditLog entries, ordered by most recent first.
    """
    return (
        session.query(AuditLog)
        .filter(AuditLog.user == user)  # type: ignore[arg-type]
        .order_by(desc(AuditLog.timestamp))  # type: ignore[arg-type]
        .limit(limit)
        .all()
    )
