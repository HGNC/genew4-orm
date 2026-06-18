"""Integration tests for genew4_orm.session module functions.

This module tests engine initialization, session factories,
read-only session behavior, and session lifecycle.
"""

import time
from contextlib import contextmanager

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


@contextmanager
def _preserve_session_state():
    """Snapshot the module-level session singletons and restore them on exit.

    Shared by the ``initialized_engine`` fixture and the close-all-sessions
    tests, which all mutate the singletons and must not leak that state into
    sibling tests.
    """
    from genew4_orm import session as session_module

    saved = (
        session_module._engine_factory,
        session_module._session_factory,
        session_module._global_settings,
    )
    try:
        yield session_module
    finally:
        (
            session_module._engine_factory,
            session_module._session_factory,
            session_module._global_settings,
        ) = saved


@pytest.fixture(scope="function")
def initialized_engine():
    """Initialize the genew4_orm.session engine for testing.

    This fixture initializes the module-level EngineFactory/SessionFactory
    singletons and restores state after each test.
    """
    with _preserve_session_state():
        initialize_engine()
        yield


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

            # Attempting to commit should raise ReadOnlySessionError.
            # The message comes from db-common's before_commit hook (delegated
            # to via SessionFactory.get_readonly_session), so we don't pin
            # the exact wording here — only the exception type.
            with pytest.raises(ReadOnlySessionError):
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
        with _preserve_session_state() as session_module:
            # First ensure we're initialized
            if session_module._engine_factory is None:
                initialize_engine()

            # Call close_all_sessions
            close_all_sessions()

            # Verify globals were reset
            assert session_module._engine_factory is None
            assert session_module._session_factory is None
            assert session_module._global_settings is None

    def test_close_all_sessions_idempotent(self) -> None:
        """Test that close_all_sessions can be called multiple times."""
        with _preserve_session_state() as session_module:
            # First ensure we're initialized
            if session_module._engine_factory is None:
                initialize_engine()

            # First call, then a second call that must not error
            close_all_sessions()
            close_all_sessions()
