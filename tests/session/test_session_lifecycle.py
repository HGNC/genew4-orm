"""Test SQLAlchemy session lifecycle and behavior."""

import time

import pytest
from sqlalchemy import text


@pytest.mark.usefixtures("postgres_session")
class TestSessionLifecycle:
    """Test SQLAlchemy session lifecycle and behavior."""

    def test_session_basic_insert_and_select(self, postgres_session):
        """Test basic session insert and select operations."""
        ts = int(time.time() * 1000)

        # Create a test gene group
        postgres_session.execute(
            text("INSERT INTO family_new (name, status) VALUES (:name, 'internal')"),
            {"name": f"test_insert_{ts}"},
        )
        postgres_session.commit()

        # Verify the data was inserted
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
            {"name": f"test_insert_{ts}"},
        ).scalar()
        assert result == 1

    def test_session_update_operations(self, postgres_session):
        """Test session update operations."""
        ts = int(time.time() * 1000)

        # Create a test gene group
        postgres_session.execute(
            text("INSERT INTO family_new (name, status) VALUES (:name, 'internal')"),
            {"name": f"update_test_{ts}"},
        )
        postgres_session.commit()

        # Update the record
        postgres_session.execute(
            text("UPDATE family_new SET name = :new_name WHERE name = :old_name"),
            {"new_name": f"update_test_updated_{ts}", "old_name": f"update_test_{ts}"},
        )
        postgres_session.commit()

        # Verify the update
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
            {"name": f"update_test_updated_{ts}"},
        ).scalar()
        assert result == 1

        # Old name should not exist
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
            {"name": f"update_test_{ts}"},
        ).scalar()
        assert result == 0

    def test_session_delete_operations(self, postgres_session):
        """Test session delete operations."""
        ts = int(time.time() * 1000)

        # Create a test gene group
        postgres_session.execute(
            text("INSERT INTO family_new (name, status) VALUES (:name, 'internal')"),
            {"name": f"delete_test_{ts}"},
        )
        postgres_session.commit()

        # Verify it exists
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
            {"name": f"delete_test_{ts}"},
        ).scalar()
        assert result == 1

        # Delete the record
        postgres_session.execute(
            text("DELETE FROM family_new WHERE name = :name"),
            {"name": f"delete_test_{ts}"},
        )
        postgres_session.commit()

        # Verify deletion
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
            {"name": f"delete_test_{ts}"},
        ).scalar()
        assert result == 0

    def test_session_rollback(self, postgres_session):
        """Test session rollback behavior."""
        ts = int(time.time() * 1000)

        # Get initial count
        initial_count = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name LIKE :pattern"),
            {"pattern": f"rollback_%{ts}%"},
        ).scalar()

        # Create a record
        postgres_session.execute(
            text("INSERT INTO family_new (name, status) VALUES (:name, 'internal')"),
            {"name": f"rollback_test_{ts}"},
        )

        # Rollback the transaction
        postgres_session.rollback()

        # After rollback, count should be same as initial
        final_count = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name LIKE :pattern"),
            {"pattern": f"rollback_%{ts}%"},
        ).scalar()

        assert final_count == initial_count

    def test_session_multiple_operations(self, postgres_session):
        """Test multiple operations in a single transaction."""
        ts = int(time.time() * 1000)

        # Create multiple records
        for i in range(5):
            postgres_session.execute(
                text("INSERT INTO family_new (name, status) VALUES (:name, 'internal')"),
                {"name": f"multi_op_{ts}_{i}"},
            )

        postgres_session.commit()

        # Verify all records were created
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name LIKE :pattern"),
            {"pattern": f"multi_op_{ts}%"},
        ).scalar()
        assert result == 5

        # Update all records
        postgres_session.execute(
            text("UPDATE family_new SET name = name || '_updated' WHERE name LIKE :pattern"),
            {"pattern": f"multi_op_{ts}%"},
        )
        postgres_session.commit()

        # Verify updates
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name LIKE :pattern"),
            {"pattern": f"multi_op_{ts}%_updated"},
        ).scalar()
        assert result == 5

        # Delete all records
        postgres_session.execute(
            text("DELETE FROM family_new WHERE name LIKE :pattern"),
            {"pattern": f"multi_op_{ts}%_updated"},
        )
        postgres_session.commit()

        # Verify deletion
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_new WHERE name LIKE :pattern"),
            {"pattern": f"multi_op_{ts}%"},
        ).scalar()
        assert result == 0
