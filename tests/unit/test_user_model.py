"""Unit tests for User model."""

from genew4_orm.models.user import User


class TestUserModel:
    """Test cases for User model."""

    def test_user_instantiation_minimal(self) -> None:
        """Test User can be instantiated with minimal required fields."""
        user = User(display_name="testuser")

        assert user.display_name == "testuser"
        assert user.id is None
        assert user.current is True  # default value

    def test_user_instantiation_full(self) -> None:
        """Test User can be instantiated with all fields."""
        user = User(
            id=1,
            display_name="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="hashed_password",
            current=True,
            jwt_refresh="refresh_token",
        )

        assert user.id == 1
        assert user.display_name == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        assert user.current is True
        assert user.jwt_refresh == "refresh_token"

    def test_user_repr(self) -> None:
        """Test User __repr__ method."""
        user = User(id=123, display_name="testuser")

        repr_str = repr(user)

        assert "User" in repr_str
        assert "id=123" in repr_str
        assert "testuser" in repr_str

    def test_user_repr_without_id(self) -> None:
        """Test User __repr__ method when id is None."""
        user = User(display_name="testuser")

        repr_str = repr(user)

        assert "User" in repr_str
        assert "id=None" in repr_str
        assert "testuser" in repr_str

    def test_user_full_name_with_first_and_last(self) -> None:
        """Test User.full_name when first_name and last_name are set."""
        user = User(
            display_name="testuser",
            first_name="John",
            last_name="Doe",
        )

        full_name = user.full_name

        assert full_name == "John Doe"

    def test_user_full_name_with_only_first_name(self) -> None:
        """Test User.full_name when only first_name is set."""
        user = User(
            display_name="testuser",
            first_name="John",
        )

        full_name = user.full_name

        # Falls back to display_name when last_name is not set
        assert full_name == "testuser"

    def test_user_full_name_with_only_last_name(self) -> None:
        """Test User.full_name when only last_name is set."""
        user = User(
            display_name="testuser",
            last_name="Doe",
        )

        full_name = user.full_name

        # Falls back to display_name when first_name is not set
        assert full_name == "testuser"

    def test_user_full_name_with_none_names(self) -> None:
        """Test User.full_name when both names are None."""
        user = User(display_name="testuser")

        full_name = user.full_name

        # Falls back to display_name when both are None
        assert full_name == "testuser"

    def test_user_full_name_with_empty_strings(self) -> None:
        """Test User.full_name with empty string names."""
        user = User(
            display_name="testuser",
            first_name="",
            last_name="",
        )

        full_name = user.full_name

        # Empty strings are falsy, so falls back to display_name
        assert full_name == "testuser"

    def test_user_full_name_with_middle_initial(self) -> None:
        """Test User.full_name includes both first and last name."""
        user = User(
            display_name="testuser",
            first_name="John Q.",
            last_name="Public",
        )

        full_name = user.full_name

        assert full_name == "John Q. Public"

    def test_user_current_default(self) -> None:
        """Test User.current field defaults to True."""
        user = User(display_name="testuser")

        assert user.current is True

    def test_user_current_can_be_false(self) -> None:
        """Test User.current can be set to False."""
        user = User(display_name="testuser", current=False)

        assert user.current is False

    def test_user_optional_fields_are_none(self) -> None:
        """Test that optional fields default to None."""
        user = User(display_name="testuser")

        assert user.first_name is None
        assert user.last_name is None
        assert user.email is None
        assert user.password is None
        assert user.jwt_refresh is None

    def test_user_table_name(self) -> None:
        """Test User table name is 'user'."""
        assert User.__tablename__ == "user"
