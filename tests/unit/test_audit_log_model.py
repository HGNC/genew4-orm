"""Unit tests for AuditLog model."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from genew4_orm.models.audit_log import (
    AuditLog,
    _deserialize_field_changes,
    _serialize_field_changes,
)


class TestSerializeFieldChanges:
    """Test cases for _serialize_field_changes function."""

    def test_serialize_field_changes_with_dict(self) -> None:
        """Test _serialize_field_changes with a dict."""
        changes = {
            "approved_symbol": {"old": None, "new": "TEST"},
            "status": {"old": "Pending", "new": "Approved"},
        }

        result = _serialize_field_changes(changes)

        assert isinstance(result, str)
        assert "approved_symbol" in result
        assert "TEST" in result

    def test_serialize_field_changes_with_empty_dict(self) -> None:
        """Test _serialize_field_changes with empty dict."""
        result = _serialize_field_changes({})

        assert result == "{}"

    def test_serialize_field_changes_with_none(self) -> None:
        """Test _serialize_field_changes with None value."""
        result = _serialize_field_changes(None)

        assert result is None

    def test_serialize_field_changes_with_nested_dict(self) -> None:
        """Test _serialize_field_changes with nested dict."""
        changes = {
            "field1": {"old": {"nested": "value"}, "new": {"nested": "updated"}},
        }

        result = _serialize_field_changes(changes)

        assert isinstance(result, str)
        assert "nested" in result


class TestDeserializeFieldChanges:
    """Test cases for _deserialize_field_changes function."""

    def test_deserialize_field_changes_with_json_string(self) -> None:
        """Test _deserialize_field_changes with valid JSON string."""
        json_str = '{"approved_symbol": {"old": null, "new": "TEST"}}'

        result = _deserialize_field_changes(json_str)

        assert isinstance(result, dict)
        assert result["approved_symbol"]["old"] is None
        assert result["approved_symbol"]["new"] == "TEST"

    def test_deserialize_field_changes_with_empty_json(self) -> None:
        """Test _deserialize_field_changes with empty JSON object."""
        result = _deserialize_field_changes("{}")

        assert result == {}

    def test_deserialize_field_changes_with_none(self) -> None:
        """Test _deserialize_field_changes with None value."""
        result = _deserialize_field_changes(None)

        assert result == {}

    def test_deserialize_field_changes_with_complex_json(self) -> None:
        """Test _deserialize_field_changes with complex JSON."""
        json_str = '{"field1": {"old": "value1", "new": "value2"}, "field2": {"old": null, "new": "value3"}}'

        result = _deserialize_field_changes(json_str)

        assert result["field1"]["old"] == "value1"
        assert result["field1"]["new"] == "value2"
        assert result["field2"]["old"] is None
        assert result["field2"]["new"] == "value3"


class TestAuditLogModel:
    """Test cases for AuditLog model."""

    def test_audit_log_instantiation(self) -> None:
        """Test AuditLog can be instantiated with all fields."""
        audit = AuditLog(
            id=1,
            timestamp=datetime.utcnow(),
            user="test_user",
            operation="CREATE",
            entity_type="Gene",
            entity_id=123,
            field_changes={"approved_symbol": {"old": None, "new": "TEST"}},
        )

        assert audit.id == 1
        assert audit.user == "test_user"
        assert audit.operation == "CREATE"
        assert audit.entity_type == "Gene"
        assert audit.entity_id == 123
        assert audit.field_changes["approved_symbol"]["new"] == "TEST"

    def test_audit_log_default_values(self) -> None:
        """Test AuditLog with default values."""
        audit = AuditLog(
            user="test_user",
            operation="UPDATE",
            entity_type="Gene",
            entity_id=123,
        )

        assert audit.id is None  # default
        assert audit.field_changes == {}  # default
        assert isinstance(audit.timestamp, datetime)

    def test_audit_log_repr(self) -> None:
        """Test AuditLog __repr__ method."""
        audit = AuditLog(
            id=1,
            user="test_user",
            operation="CREATE",
            entity_type="Gene",
            entity_id=123,
        )

        repr_str = repr(audit)

        assert "AuditLog" in repr_str
        assert "id=1" in repr_str
        assert "CREATE" in repr_str
        assert "Gene" in repr_str
        assert "entity_id=123" in repr_str

    def test_audit_log_get_field_diff(self) -> None:
        """Test AuditLog.get_field_diff method."""
        audit = AuditLog(
            user="test_user",
            operation="UPDATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={
                "approved_name": {"old": "Old Name", "new": "New Name"},
                "status": {"old": "Pending", "new": "Approved"},
            },
        )

        name_diff = audit.get_field_diff("approved_name")
        assert name_diff == {"old": "Old Name", "new": "New Name"}

        status_diff = audit.get_field_diff("status")
        assert status_diff == {"old": "Pending", "new": "Approved"}

        nonexistent = audit.get_field_diff("nonexistent")
        assert nonexistent is None

    def test_audit_log_get_field_diff_with_empty_field_changes(self) -> None:
        """Test AuditLog.get_field_diff with empty field_changes."""
        audit = AuditLog(
            user="test_user",
            operation="CREATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={},
        )

        result = audit.get_field_diff("any_field")
        assert result is None

    def test_audit_log_get_changed_fields(self) -> None:
        """Test AuditLog.get_changed_fields method."""
        audit = AuditLog(
            user="test_user",
            operation="UPDATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={
                "approved_name": {"old": "Old", "new": "New"},
                "status": {"old": "Pending", "new": "Approved"},
                "symbol": {"old": "OLD", "new": "NEW"},
            },
        )

        changed = audit.get_changed_fields()

        assert set(changed) == {"approved_name", "status", "symbol"}

    def test_audit_log_get_changed_fields_empty(self) -> None:
        """Test AuditLog.get_changed_fields with no changes."""
        audit = AuditLog(
            user="test_user",
            operation="CREATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={},
        )

        changed = audit.get_changed_fields()

        assert changed == []

    def test_audit_log_field_changes_dict_type(self) -> None:
        """Test that field_changes is a dict type."""
        audit = AuditLog(
            user="test_user",
            operation="UPDATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={"field1": {"old": "a", "new": "b"}},
        )

        assert isinstance(audit.field_changes, dict)
        assert "field1" in audit.field_changes

    def test_audit_log_operation_types(self) -> None:
        """Test AuditLog with different operation types."""
        for op in ["CREATE", "UPDATE", "DELETE"]:
            audit = AuditLog(
                user="test_user",
                operation=op,
                entity_type="Gene",
                entity_id=1,
            )
            assert audit.operation == op


class TestAuditLogFieldChangesRoundTrip:
    """field_changes round-trips through the database as a dict.

    `field_changes` is declared `Mapped[dict]` and the accessors
    `get_field_diff` / `get_changed_fields` assume a dict. This only holds if a
    row loaded from the DB deserializes its stored JSON text back into a dict;
    the in-memory tests above do not exercise that path.
    """

    @staticmethod
    def _commit_and_reload(session: SQLAlchemySession, field_changes: dict[str, Any]) -> AuditLog:
        """Insert an AuditLog row, commit, and reload it from the database."""
        session.add(
            AuditLog(
                user="test_user",
                operation="CREATE",
                entity_type="Gene",
                entity_id=1,
                field_changes=field_changes,
            )
        )
        session.commit()
        return session.execute(select(AuditLog).where(AuditLog.entity_type == "Gene")).scalar_one()

    def test_field_changes_is_dict_after_load(self, sqlite_session: SQLAlchemySession) -> None:
        """field_changes must deserialize to a dict on DB load (not a JSON str)."""
        loaded = self._commit_and_reload(sqlite_session, {"approved_symbol": {"old": None, "new": "ROUNDTRIP_TEST"}})
        assert isinstance(loaded.field_changes, dict)

    def test_field_changes_dict_access(self, sqlite_session: SQLAlchemySession) -> None:
        """field_changes can be keyed directly on a DB-loaded row."""
        loaded = self._commit_and_reload(sqlite_session, {"approved_symbol": {"old": None, "new": "ROUNDTRIP_TEST"}})
        assert loaded.field_changes["approved_symbol"]["new"] == "ROUNDTRIP_TEST"

    def test_get_field_diff_works_after_load(self, sqlite_session: SQLAlchemySession) -> None:
        """get_field_diff must not raise on a DB-loaded row."""
        loaded = self._commit_and_reload(
            sqlite_session,
            {"status": {"old": "Pending", "new": "Approved"}},
        )
        assert loaded.get_field_diff("status") == {"old": "Pending", "new": "Approved"}
        assert loaded.get_field_diff("missing") is None

    def test_get_changed_fields_works_after_load(self, sqlite_session: SQLAlchemySession) -> None:
        """get_changed_fields must not raise on a DB-loaded row."""
        loaded = self._commit_and_reload(
            sqlite_session,
            {
                "approved_symbol": {"old": None, "new": "ROUNDTRIP_TEST"},
                "status": {"old": "Pending", "new": "Approved"},
            },
        )
        assert set(loaded.get_changed_fields()) == {"approved_symbol", "status"}
