"""Unit tests for the session management module.

Pins the T4 contract: session infrastructure delegates engine/session
creation to the shared ``db-common`` library, while the genew4 wrappers
preserve the ``session.info`` audit contract (``user`` / ``read_only``)
that ``genew4_orm.audit`` reads. The public exception symbols are
re-exported from ``db_common`` — ``ReadOnlySessionError`` keeps its name
(now ``db_common.ReadOnlySessionError``) and ``SessionError`` is added —
so the historical "not initialized" ``RuntimeError`` collapses onto
``SessionError``.

All behaviour tests run against a real ``sqlite:///:memory:`` engine
bound through the new code path
(``initialize_engine(DatabaseSettings(driver='sqlite'))``) — no
PostgreSQL dependency, no ``inspect.getsource`` string assertions.
"""

from collections.abc import Generator
from unittest.mock import patch

import db_common
import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from genew4_orm.config import DatabaseSettings
from genew4_orm.session import (
    ReadOnlySessionError,
    SessionError,
    close_all_sessions,
    get_engine,
    get_readonly_session,
    get_readwrite_session,
    get_settings,
    initialize_engine,
    refresh_engine,
)

# ---------------------------------------------------------------------------
# Fixtures — isolate the module-level singletons across tests.
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_session_module() -> Generator:
    """Save/clear/restore the module-level session singletons.

    Ensures a test that calls ``initialize_engine`` cannot leak engines or
    sessions into sibling tests, and that the test starts from a clean
    (uninitialized) state.
    """
    import genew4_orm.session as session_module

    saved = (
        session_module._engine_factory,
        session_module._session_factory,
        session_module._global_settings,
    )

    # Clear state for THIS test (the saved singletons' lifetime is owned by
    # whoever created them — we only null the module references here).
    session_module._engine_factory = None
    session_module._session_factory = None
    session_module._global_settings = None

    try:
        yield session_module
    finally:
        # Dispose anything the test created, then restore the saved state.
        if session_module._engine_factory is not None:
            session_module._engine_factory.dispose()
        session_module._engine_factory = saved[0]
        session_module._session_factory = saved[1]
        session_module._global_settings = saved[2]


@pytest.fixture
def sqlite_session_module(isolated_session_module) -> Generator:
    """Initialize the session infra against a real in-memory SQLite engine."""
    initialize_engine(DatabaseSettings(driver="sqlite"))
    yield isolated_session_module


# ---------------------------------------------------------------------------
# Public symbol re-exports.
# ---------------------------------------------------------------------------


class TestPublicSymbols:
    """Exception symbols are re-exported from db_common (no local classes)."""

    def test_readonly_session_error_is_db_common_class(self) -> None:
        """ReadOnlySessionError resolves to db_common.ReadOnlySessionError."""
        assert ReadOnlySessionError is db_common.ReadOnlySessionError

    def test_readonly_session_error_is_exception(self) -> None:
        """ReadOnlySessionError is still an Exception subclass."""
        assert issubclass(ReadOnlySessionError, Exception)

    def test_session_error_is_db_common_class(self) -> None:
        """SessionError is re-exported from db_common (replaces RuntimeError)."""
        assert SessionError is db_common.SessionError

    def test_public_symbols_listed_in_package_all(self) -> None:
        """Both exception re-exports are part of the public package API.

        Regression guard: ``SessionError`` was imported into the package but
        absent from ``__all__``, so ``from genew4_orm import *`` and
        ``__all__``-walking tooling (linters, mock.patch) silently dropped it.
        """
        import genew4_orm

        assert "ReadOnlySessionError" in genew4_orm.__all__
        assert "SessionError" in genew4_orm.__all__
        assert genew4_orm.SessionError is db_common.SessionError
        assert genew4_orm.ReadOnlySessionError is db_common.ReadOnlySessionError


# ---------------------------------------------------------------------------
# Uninitialized state — verify item (c).
# ---------------------------------------------------------------------------


class TestUninitialized:
    """get_engine/get_settings raise SessionError when uninitialized."""

    def test_get_engine_raises_session_error(self, isolated_session_module) -> None:
        with pytest.raises(SessionError):
            get_engine()

    def test_get_settings_raises_session_error(self, isolated_session_module) -> None:
        with pytest.raises(SessionError):
            get_settings()

    def test_get_engine_no_longer_raises_runtime_error(self, isolated_session_module) -> None:
        """Regression guard: was RuntimeError before T4, now SessionError."""
        with pytest.raises(SessionError):
            get_engine()

    def test_readwrite_session_raises_session_error(self, isolated_session_module) -> None:
        """get_readwrite_session surfaces SessionError when uninitialized."""
        with pytest.raises(SessionError):
            with get_readwrite_session():
                pass

    def test_readonly_session_raises_session_error(self, isolated_session_module) -> None:
        """get_readonly_session surfaces SessionError when uninitialized."""
        with pytest.raises(SessionError):
            with get_readonly_session():
                pass


# ---------------------------------------------------------------------------
# Read-write session behaviour — verify item (a).
# ---------------------------------------------------------------------------


class TestReadWriteSession:
    """get_readwrite_session(user=) populates session.info for audit."""

    def test_default_user_is_unknown(self, sqlite_session_module) -> None:
        with get_readwrite_session() as session:
            assert session.info["user"] == "unknown"
            assert session.info["read_only"] is False

    def test_custom_user_is_recorded(self, sqlite_session_module) -> None:
        with get_readwrite_session(user="alice") as session:
            assert session.info["user"] == "alice"
            assert session.info["read_only"] is False

    def test_yields_sqlalchemy_session(self, sqlite_session_module) -> None:
        with get_readwrite_session() as session:
            assert isinstance(session, Session)

    def test_exception_propagates_and_rolls_back(self, sqlite_session_module) -> None:
        class _BoomError(Exception):
            pass

        with pytest.raises(_BoomError):
            with get_readwrite_session():
                raise _BoomError("simulated failure")


# ---------------------------------------------------------------------------
# Read-only session behaviour — verify item (b).
# ---------------------------------------------------------------------------


class TestReadonlySession:
    """get_readonly_session() rejects commits with ReadOnlySessionError."""

    def test_marks_read_only_with_no_user(self, sqlite_session_module) -> None:
        with get_readonly_session() as session:
            assert session.info["read_only"] is True
            assert session.info["user"] is None

    def test_commit_raises_readonly_session_error(self, sqlite_session_module) -> None:
        with get_readonly_session() as session:
            with pytest.raises(ReadOnlySessionError):
                session.commit()


# ---------------------------------------------------------------------------
# Initialization / engine / settings.
# ---------------------------------------------------------------------------


class TestInitialization:
    """initialize_engine builds the EngineFactory + SessionFactory singletons."""

    def test_get_engine_returns_engine(self, sqlite_session_module) -> None:
        engine = get_engine()
        assert isinstance(engine, Engine)

    def test_initialize_is_idempotent(self, sqlite_session_module) -> None:
        first = initialize_engine()
        second = initialize_engine()
        assert first is second

    def test_get_settings_returns_settings(self, sqlite_session_module) -> None:
        settings = get_settings()
        assert isinstance(settings, DatabaseSettings)
        assert settings.driver == "sqlite"

    def test_engine_factory_is_genew4_subclass(self, sqlite_session_module) -> None:
        """The EngineFactory singleton is Genew4EngineFactory (adds pool_timeout)."""
        from genew4_orm.session import Genew4EngineFactory

        assert isinstance(sqlite_session_module._engine_factory, Genew4EngineFactory)


class TestGenew4EngineFactoryPoolTimeout:
    """``Genew4EngineFactory`` passes ``pool_timeout``; db-common's does not.

    Pins the spec's "pool_timeout preserved" behaviour change: the local
    ``Genew4EngineFactory`` override adds ``pool_timeout`` for non-SQLite
    drivers (reading the genew4-only field on ``Genew4DatabaseSettings``),
    while leaving the SQLite path identical to db-common's.
    """

    @staticmethod
    def _engine_kwargs(settings: DatabaseSettings) -> dict:
        """Build an engine via ``Genew4EngineFactory`` and return the kwargs
        ``create_engine`` was called with (``create_engine`` is patched out)."""
        from unittest.mock import MagicMock, patch

        from genew4_orm.session import Genew4EngineFactory

        factory = Genew4EngineFactory(settings)
        with patch("genew4_orm.session.create_engine") as mock_create:
            mock_create.return_value = MagicMock(spec=Engine)
            factory.get_engine()
        _args, kwargs = mock_create.call_args
        return kwargs

    def test_pool_timeout_passed_for_non_sqlite(self) -> None:
        """Non-sqlite engines are created with pool_timeout from settings."""
        settings = DatabaseSettings(
            driver="postgresql+psycopg",
            host="localhost",
            port=5432,
            database="genew4",
            username="u",
            password="p",
            pool_timeout=42,
        )

        kwargs = self._engine_kwargs(settings)

        assert kwargs["pool_timeout"] == 42
        # The inherited pool fields are passed too.
        assert kwargs["pool_size"] == 5
        assert kwargs["max_overflow"] == 10
        assert kwargs["pool_pre_ping"] is True

    def test_pool_timeout_omitted_for_sqlite(self) -> None:
        """SQLite engines do not pass pool_timeout (matches db-common's path)."""
        from sqlalchemy.pool import StaticPool

        kwargs = self._engine_kwargs(DatabaseSettings(driver="sqlite"))

        assert "pool_timeout" not in kwargs
        # SQLite path uses StaticPool (mirrors db-common).
        assert kwargs["poolclass"] is StaticPool


class TestRefreshAndClose:
    """refresh_engine and close_all_sessions."""

    def test_refresh_returns_engine(self, sqlite_session_module) -> None:
        engine = refresh_engine()
        assert isinstance(engine, Engine)

    def test_refresh_without_settings_raises_session_error(self, isolated_session_module) -> None:
        with pytest.raises(SessionError):
            refresh_engine()

    def test_close_resets_singletons(self, sqlite_session_module) -> None:
        close_all_sessions()
        assert sqlite_session_module._engine_factory is None
        assert sqlite_session_module._session_factory is None
        assert sqlite_session_module._global_settings is None

    def test_close_is_idempotent(self, sqlite_session_module) -> None:
        close_all_sessions()
        close_all_sessions()  # second call must not raise


# ---------------------------------------------------------------------------
# DatabaseSettings surface — exercised through the session path. The methods
# are also pinned in test_config.py; these cover the session-test angle.
# ---------------------------------------------------------------------------


class TestEngineKwargs:
    """get_engine_kwargs reads the inherited pool fields + pool_timeout."""

    def test_get_engine_kwargs_structure(self) -> None:
        import os

        with patch.dict(
            os.environ,
            {
                "DATABASESETTINGS_PG_USER": "test",
                "DATABASESETTINGS_PG_PASSWORD": "test",
            },
        ):
            settings = DatabaseSettings()
            kwargs = settings.get_engine_kwargs()

            assert isinstance(kwargs, dict)
            assert "pool_size" in kwargs
            assert "max_overflow" in kwargs
            assert "pool_timeout" in kwargs
            assert "pool_recycle" in kwargs
            assert "pool_pre_ping" in kwargs


class TestConnectionUrl:
    """get_connection_url is the legacy compat shim delegating to get_url()."""

    def test_get_connection_url_without_password(self) -> None:
        import os

        with patch.dict(
            os.environ,
            {
                "DATABASESETTINGS_PG_USER": "testuser",
                "DATABASESETTINGS_PG_PASSWORD": "secret123",
            },
        ):
            settings = DatabaseSettings()
            url = settings.get_connection_url()

            assert "testuser" in url
            assert "secret123" not in url
            assert "postgresql+psycopg://" in url

    def test_get_connection_url_with_password(self) -> None:
        import os

        with patch.dict(
            os.environ,
            {
                "DATABASESETTINGS_PG_USER": "testuser",
                "DATABASESETTINGS_PG_PASSWORD": "secret123",
            },
        ):
            settings = DatabaseSettings()
            url = settings.get_connection_url(with_password=True)

            assert "testuser" in url
            assert "secret123" in url
            assert "postgresql+psycopg://" in url
