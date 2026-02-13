"""Additional unit tests for User model to improve coverage."""

import pytest

from genew4_orm.models import User


class TestUserFullName:
    """Test cases for User.full_name property."""

    def test_full_name_with_first_and_last(self) -> None:
        """Test full_name returns first + last name."""
        user = User(
            first_name="John",
            last_name="Doe",
            login="johndoe",
            display_name="John Doe",
        )

        assert user.full_name == "John Doe"

    def test_full_name_with_first_only(self) -> None:
        """Test full_name returns first name when last is None."""
        user = User(
            first_name="John",
            last_name=None,
            login="johndoe",
            display_name="John",
        )

        assert user.full_name == "John"

    def test_full_name_with_last_only(self) -> None:
        """Test full_name returns last name when first is None."""
        user = User(
            first_name=None,
            last_name="Doe",
            login="doe",
            display_name="Doe",
        )

        assert user.full_name == "Doe"

    def test_full_name_with_display_name_fallback(self) -> None:
        """Test full_name returns display_name when both first and last are None."""
        user = User(
            first_name=None,
            last_name=None,
            login="user123",
            display_name="Display Name",
        )

        assert user.full_name == "Display Name"


class TestUserRepr:
    """Additional test cases for User __repr__ method."""

    def test_user_repr_with_all_fields(self) -> None:
        """Test User __repr__ includes relevant info."""
        user = User(
            id=999,
            login="testuser",
            display_name="Test User",
        )

        repr_str = repr(user)

        assert "User" in repr_str
        # Check that the repr contains the user info
        assert "999" in repr_str
