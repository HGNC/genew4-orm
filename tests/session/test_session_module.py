"""Integration tests for genew4_orm.session module functions.

This module tests engine initialization, session factories,
read-only session behavior, and session lifecycle.
"""

import time

import pytest
from sqlalchemy import text

from genew4_orm.config import DatabaseSettings
from genew4_orm.session import (
    ReadOnlySessionError,
    close_all_sessions,
    get_engine,
    get_readonly_session,
    get_readwrite_session,
    get_settings,
    initialize_engine,
    refresh_engine,
)


@pytest.fixture(scope="function")
def initialized_engine():
    """Initialize the genew4_orm.session engine for testing.

    This fixture initializes the module-level engine and restores
    state after each test.
    """
    from genew4_orm import session as session_module

    original_engine = session_module._global_engine
    original_settings = session_module._global_settings
    original_session_factory = session_module._session_factory
    original_readonly_factory = session_module._readonly_session_factory

    # Initialize the engine
    initialize_engine()

    yield

    # Restore original state after test
    session_module._global_engine = original_engine
    session_module._global_settings = original_settings
    session_module._session_factory = original_session_factory
    session_module._readonly_session_factory = original_readonly_factory


class TestEngineFunctions:
    """Test database engine functions."""

    def test_get_engine_returns_initialized_engine(self, initialized_engine) -> None:
        """Test that get_engine returns the initialized engine."""
        engine = get_engine()
        assert engine is not None

    def test_initialize_engine_returns_same_instance(self, initialized_engine) -> None:
        """Test that initialize_engine returns same instance on subsequent calls."""
        # First call was done by fixture
        # Second call should return same instance
        engine2 = initialize_engine()
        engine1 = get_engine()
        assert engine1 is engine2

    def test_get_settings_returns_database_settings(self, initialized_engine) -> None:
        """Test that get_settings returns DatabaseSettings instance."""
        settings = get_settings()
        assert settings is not None
        assert isinstance(settings, DatabaseSettings)


class TestReadWriteSession:
    """Test read-write session behavior."""

    def test_readwrite_session_with_user_context(self, initialized_engine) -> None:
        """Test that user context is stored in session info."""
        with get_readwrite_session(user="test_user") as session:
            # User should be in session info
            assert session.info.get("user") == "test_user"
            # Should not be read-only
            assert session.info.get("read_only") is False

    def test_readwrite_session_default_user(self, initialized_engine) -> None:
        """Test that readwrite session uses 'unknown' as default user."""
        with get_readwrite_session() as session:
            # Default user should be 'unknown'
            assert session.info.get("user") == "unknown"


class TestReadOnlySession:
    """Test read-only session behavior."""

    def test_readonly_session_prevents_commit(self, initialized_engine) -> None:
        """Test that read-only session raises error on commit attempt."""
        with get_readonly_session() as session:
            # Marked as read-only
            assert session.info.get("read_only") is True
            # User should be None for read-only
            assert session.info.get("user") is None

            # Attempting to commit should raise ReadOnlySessionError
            with pytest.raises(ReadOnlySessionError, match="Cannot commit changes"):
                session.commit()

    def test_readonly_session_allows_queries(self, initialized_engine) -> None:
        """Test that read-only session allows read operations."""
        ts = int(time.time() * 1000)

        # Create a test record first
        with get_readwrite_session() as session:
            session.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"readonly_test_{ts}"},
            )

        # Now query with read-only session
        with get_readonly_session() as session:
            result = session.execute(
                text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
                {"name": f"readonly_test_{ts}"},
            ).scalar()
            assert result == 1


class TestSessionIntegration:
    """Integration tests for session behavior across operations."""

    def test_multiple_readwrite_sessions_independently(self, initialized_engine) -> None:
        """Test that multiple readwrite sessions work independently."""
        ts = int(time.time() * 1000)

        # First session creates a record
        with get_readwrite_session(user="user1") as session1:
            session1.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"multi_session_test_{ts}"},
            )

        # Second session should see the record
        with get_readwrite_session(user="user2") as session2:
            result = session2.execute(
                text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
                {"name": f"multi_session_test_{ts}"},
            ).scalar()
            assert result == 1

    def test_session_isolation_between_operations(self, initialized_engine) -> None:
        """Test that sessions are properly isolated."""
        ts = int(time.time() * 1000)

        # Create in one session
        with get_readwrite_session(user="user1") as session1:
            session1.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"isolation_test_{ts}"},
            )

        # Different session should see committed data
        with get_readonly_session() as session2:
            result = session2.execute(
                text("SELECT COUNT(*) FROM family_new WHERE name = :name"),
                {"name": f"isolation_test_{ts}"},
            ).scalar()
            # Should be 1 since first session committed
            assert result == 1


class TestRefreshEngine:
    """Test engine refresh functionality."""

    def test_refresh_engine_returns_engine(self, initialized_engine) -> None:
        """Test that refresh_engine returns an engine."""
        new_engine = refresh_engine()
        assert new_engine is not None


class TestCloseAllSessions:
    """Test session cleanup functionality."""

    def test_close_all_sessions_handles_initialized_state(self) -> None:
        """Test that close_all_sessions works with initialized engine."""
        from genew4_orm import session as session_module

        # Store original values for restoration
        original_engine = session_module._global_engine
        original_session_factory = session_module._session_factory
        original_readonly_factory = session_module._readonly_session_factory

        # First ensure we're initialized
        if session_module._global_engine is None:
            initialize_engine()

        # Call close_all_sessions
        close_all_sessions()

        # Verify globals were reset
        assert session_module._global_engine is None
        assert session_module._session_factory is None
        assert session_module._readonly_session_factory is None

        # Restore for other tests
        session_module._global_engine = original_engine
        session_module._session_factory = original_session_factory
        session_module._readonly_session_factory = original_readonly_factory

    def test_close_all_sessions_idempotent(self) -> None:
        """Test that close_all_sessions can be called multiple times."""
        from genew4_orm import session as session_module

        # Store original values for restoration
        original_engine = session_module._global_engine
        original_session_factory = session_module._session_factory
        original_readonly_factory = session_module._readonly_session_factory

        # First ensure we're initialized
        if session_module._global_engine is None:
            initialize_engine()

        try:
            # First call
            close_all_sessions()
            # Second call should not error
            close_all_sessions()
        finally:
            # Restore for other tests
            session_module._global_engine = original_engine
            session_module._session_factory = original_session_factory
            session_module._readonly_session_factory = original_readonly_factory
