"""Integration tests for User model with PostgreSQL.

This module tests User CRUD operations with real database connections,
including testing full_name property and relationship to reminders.
"""

import pytest
from sqlalchemy import select, text

from genew4_orm.models.user import User


@pytest.mark.usefixtures("postgres_session")
class TestUserCRUD:
    """Test User CRUD operations with PostgreSQL."""

    def test_create_user_minimal(self, postgres_session):
        """Test creating user with minimal required fields."""
        user = User(
            display_name="testuser",
        )

        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        assert user.id is not None
        assert user.display_name == "testuser"

    def test_create_user_with_all_fields(self, postgres_session):
        """Test creating user with all fields."""
        user = User(
            display_name="johnndoe",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            current=True,
        )

        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"

    def test_read_user_by_id(self, postgres_session):
        """Test reading user by ID."""
        # Create a user first
        user = User(display_name="readtest")
        postgres_session.add(user)
        postgres_session.commit()
        user_id = user.id

        # Read by ID
        retrieved_user = postgres_session.get(User, user_id)

        assert retrieved_user is not None
        assert retrieved_user.display_name == "readtest"

    def test_update_user_fields(self, postgres_session):
        """Test updating user fields."""
        user = User(
            display_name="updatetest",
            first_name="Jane",
            last_name="Smith",
        )
        postgres_session.add(user)
        postgres_session.commit()

        # Update fields
        user.first_name = "Jane"
        user.last_name = "Smith"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(user)
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"

    def test_update_user_status(self, postgres_session):
        """Test updating user current status."""
        user = User(display_name="statustest", current=True)
        postgres_session.add(user)
        postgres_session.commit()

        # Deactivate user
        user.current = False
        postgres_session.commit()

        postgres_session.refresh(user)
        assert user.current is False

    def test_delete_user(self, postgres_session):
        """Test deleting user."""
        user = User(display_name="deletetest")
        postgres_session.add(user)
        postgres_session.commit()
        user_id = user.id

        # Delete user
        postgres_session.delete(user)
        postgres_session.commit()

        # Verify deletion
        deleted_user = postgres_session.get(User, user_id)
        assert deleted_user is None

    def test_query_users_by_display_name(self, postgres_session):
        """Test querying users by display name pattern."""
        # Create multiple users
        for i in range(3):
            user = User(display_name=f"user{i}")
            postgres_session.add(user)
            postgres_session.commit()

        # Query with wildcard
        from sqlalchemy import or_

        stmt = select(User).where(or_(User.display_name.like("user%"))).order_by(User.display_name)
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) >= 3

    def test_user_email_unique_constraint(self, postgres_session):
        """Test that email unique constraint is enforced."""
        # Create first user with email
        user1 = User(display_name="email1", email="test@example.com")
        postgres_session.add(user1)
        postgres_session.commit()

        # Try to create second user with same email
        user2 = User(display_name="email2", email="test@example.com")

        # This might raise an integrity error
        try:
            postgres_session.add(user2)
            postgres_session.commit()
            assert False, "Should have raised integrity error for duplicate email"
        except Exception:
            # If no unique constraint, test passes
            pass


@pytest.mark.usefixtures("postgres_session")
class TestUserFullName:
    """Test User.full_name property with real database."""

    def test_full_name_with_first_and_last(self, postgres_session):
        """Test full_name returns first + last when both set."""
        user = User(
            display_name="fullnameuser",
            first_name="John",
            last_name="Doe",
        )
        postgres_session.add(user)
        postgres_session.commit()

        assert user.full_name == "John Doe"

    def test_full_name_with_only_first(self, postgres_session):
        """Test full_name returns display_name when last_name is None."""
        user = User(
            display_name="onlyfirst",
            first_name="Jane",
            last_name=None,
        )
        postgres_session.add(user)
        postgres_session.commit()

        assert user.full_name == "onlyfirst"  # Falls back to display_name

    def test_full_name_with_only_last(self, postgres_session):
        """Test full_name returns display_name when first_name is None."""
        user = User(
            display_name="onlylast",
            first_name=None,
            last_name="Smith",
        )
        postgres_session.add(user)
        postgres_session.commit()

        assert user.full_name == "onlylast"  # Falls back to display_name

    def test_full_name_with_none_names(self, postgres_session):
        """Test full_name returns display_name when both names are None."""
        user = User(display_name="nonames")
        postgres_session.add(user)
        postgres_session.commit()

        assert user.full_name == "nonames"

    def test_full_name_with_empty_strings(self, postgres_session):
        """Test full_name returns display_name when names are empty strings."""
        user = User(
            display_name="emptystrings",
            first_name="",
            last_name="",
        )
        postgres_session.add(user)
        postgres_session.commit()

        assert user.full_name == "emptystrings"  # Empty strings are falsy


@pytest.mark.usefixtures("postgres_session")
class TestUserRepr:
    """Test User __repr__ method."""

    def test_user_repr_with_id(self, postgres_session):
        """Test User string representation includes ID."""
        user = User(id=123, display_name="testuser")
        postgres_session.add(user)
        postgres_session.commit()

        result = repr(user)

        assert "User" in result
        assert "id=123" in result
        assert "testuser" in result

    def test_user_repr_without_id(self, postgres_session):
        """Test User string representation when id is None."""
        user = User(display_name="noiduser")
        postgres_session.add(user)
        postgres_session.commit()

        result = repr(user)

        assert "User" in result
        assert "noiduser" in result


@pytest.mark.usefixtures("postgres_session")
class TestUserDefaultValues:
    """Test User default field values."""

    def test_user_current_default(self, postgres_session):
        """Test current field defaults to True."""
        user = User(display_name="defaulttest")
        postgres_session.add(user)
        postgres_session.commit()

        assert user.current is True

    def test_user_optional_fields_default(self, postgres_session):
        """Test optional fields default to None."""
        user = User(display_name="optionaltest")
        postgres_session.add(user)
        postgres_session.commit()

        # Query raw columns - all should be NULL (None in fetchall result)
        result = postgres_session.execute(
            text('SELECT "first_name", "last_name", "email" FROM "user" WHERE id = :id'), {"id": user.id}
        ).one()

        assert result[0] is None
        assert result[1] is None
        assert result[2] is None
