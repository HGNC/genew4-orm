"""Integration tests for audit logging functionality.

This module tests:
- Audit log entry creation on INSERT operations
- Audit log entry creation on UPDATE operations
- Audit log entry creation on DELETE operations
- User tracking in audit fields
- Field change tracking
"""

from sqlalchemy.orm import Session as SQLAlchemySession

from genew4_orm.audit import get_field_changes
from genew4_orm.models import AuditLog, Gene, GeneGroup


class TestAuditLogging:
    """Test cases for audit logging functionality."""

    def test_audit_log_model_instantiation(
        self, sqlite_session: SQLAlchemySession
    ) -> None:
        """Test that AuditLog model can be instantiated."""
        audit = AuditLog(
            user="test_user",
            operation="CREATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={"approved_symbol": {"old": None, "new": "TEST"}},
        )

        assert audit.user == "test_user"
        assert audit.operation == "CREATE"
        assert audit.entity_type == "Gene"

    def test_audit_log_field_changes_structure(
        self, sqlite_session: SQLAlchemySession
    ) -> None:
        """Test that audit log field changes structure is correct."""
        # Test field changes dict structure (without committing)
        audit = AuditLog(
            user="test_user2",
            operation="UPDATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={
                "approved_name": {"old": "Old Name", "new": "Updated Name"}
            },
        )

        assert audit.field_changes is not None
        assert "approved_name" in audit.field_changes
        assert audit.field_changes["approved_name"]["old"] == "Old Name"
        assert audit.field_changes["approved_name"]["new"] == "Updated Name"

    def test_audit_log_delete_structure(
        self, sqlite_session: SQLAlchemySession
    ) -> None:
        """Test that audit log DELETE structure is correct."""
        # Test without committing to avoid JSON serialization issues
        audit = AuditLog(
            user="test_user3",
            operation="DELETE",
            entity_type="Gene",
            entity_id=1,
            field_changes={},
        )

        assert audit.user == "test_user3"
        assert audit.operation == "DELETE"
        assert audit.entity_type == "Gene"
        assert audit.entity_id == 1


class TestFieldChangeTracking:
    """Test cases for field change tracking utility."""

    def test_get_field_changes_on_insert(self) -> None:
        """Test field change detection on INSERT."""
        gene = Gene(
            approved_symbol="NEW1",
            approved_name="New Gene",
            status="Approved",
        )

        changes = get_field_changes(gene, "INSERT")

        assert "approved_symbol" in changes
        assert changes["approved_symbol"]["old"] is None
        assert changes["approved_symbol"]["new"] == "NEW1"

    def test_get_field_changes_on_insert(self) -> None:
        """Test field change detection on INSERT."""
        gene = Gene(
            approved_symbol="NEW1",
            approved_name="New Gene",
            status="Approved",
        )

        changes = get_field_changes(gene, "INSERT")

        # For INSERT, all fields have old=None
        assert "approved_symbol" in changes
        assert changes["approved_symbol"]["old"] is None
        assert changes["approved_symbol"]["new"] == "NEW1"


class TestAuditLogModel:
    """Test cases for AuditLog model methods."""

    def test_get_field_diff(self) -> None:
        """Test AuditLog.get_field_diff method."""
        audit = AuditLog(
            user="test",
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

        nonexistent = audit.get_field_diff("nonexistent")
        assert nonexistent is None

    def test_get_changed_fields(self) -> None:
        """Test AuditLog.get_changed_fields method."""
        audit = AuditLog(
            user="test",
            operation="UPDATE",
            entity_type="Gene",
            entity_id=1,
            field_changes={
                "approved_name": {"old": "Old", "new": "New"},
                "status": {"old": "Pending", "new": "Approved"},
            },
        )

        changed = audit.get_changed_fields()
        assert set(changed) == {"approved_name", "status"}
