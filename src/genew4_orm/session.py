"""SQLAlchemy session management and engine factory.

This module delegates engine/session creation to the shared ``db-common``
library: a module-level :class:`Genew4EngineFactory` (a
``db_common.EngineFactory`` subclass that also passes ``pool_timeout``,
which db-common's own factory does not) and a ``db_common.SessionFactory``
provide the underlying engine and sessions, while the genew4 wrappers
preserve the audit-related ``session.info`` contract (``user``,
``read_only``) that :mod:`genew4_orm.audit` reads.

The seven public symbols — ``initialize_engine``, ``get_engine``,
``get_settings``, ``get_readwrite_session``, ``get_readonly_session``,
``close_all_sessions``, ``refresh_engine`` — keep their signatures.
``ReadOnlySessionError`` is re-exported from ``db_common`` so the public
name is unchanged; ``SessionError`` is re-exported alongside it, and the
"not initialized" errors collapse from the historical ``RuntimeError``
onto ``SessionError`` (a ``db_common.DatabaseError`` subclass).
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import db_common
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from genew4_orm.config.database_settings import DatabaseSettings

# Module-level singletons. Created by ``initialize_engine`` and reset by
# ``close_all_sessions``. Tests save/restore these to isolate state.
_engine_factory: "Genew4EngineFactory | None" = None
_session_factory: db_common.SessionFactory | None = None
_global_settings: DatabaseSettings | None = None


# Re-export the shared exceptions so the public symbol names are unchanged.
# ``ReadOnlySessionError`` was a local class before T4; it is now the
# db-common class of the same name. ``SessionError`` is added so callers
# can catch the "not initialized" condition without reaching into db_common.
ReadOnlySessionError = db_common.ReadOnlySessionError
SessionError = db_common.SessionError


class Genew4EngineFactory(db_common.EngineFactory):
    """Engine factory that also passes ``pool_timeout`` to ``create_engine``.

    ``db_common.EngineFactory._create_engine`` builds the engine from
    :meth:`DatabaseSettings.get_url` and the inherited pool fields, but
    does not pass ``pool_timeout`` (db-common deliberately ships no
    pool-timeout behaviour). Genew4 historically used a 30s pool timeout,
    now exposed as the ``pool_timeout`` field on
    :class:`~genew4_orm.config.database_settings.Genew4DatabaseSettings`,
    so this subclass overrides ``_create_engine`` to add ``pool_timeout``
    for non-SQLite drivers while leaving the SQLite path identical to
    db-common's (StaticPool + ``check_same_thread=False``).
    """

    def _create_engine(self) -> Engine:
        url = self._settings.get_url()
        kwargs: dict[str, Any] = {}

        if self._settings.driver == "sqlite":
            # SQLite in-memory needs StaticPool so the same connection is
            # shared across threads / sessions (mirrors db-common's logic).
            kwargs["poolclass"] = StaticPool
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            kwargs["pool_size"] = self._settings.pool_size
            kwargs["max_overflow"] = self._settings.max_overflow
            kwargs["pool_recycle"] = self._settings.pool_recycle
            kwargs["pool_pre_ping"] = self._settings.pool_pre_ping
            # genew4-only: pool_timeout is not in db-common's EngineFactory.
            kwargs["pool_timeout"] = getattr(self._settings, "pool_timeout", 30)

        return create_engine(url, **kwargs)


def initialize_engine(settings: DatabaseSettings | None = None) -> Engine:
    """Initialize the global database engine.

    Builds and caches the ``EngineFactory`` / ``SessionFactory`` singletons.
    Idempotent: a second call returns the already-cached engine.

    Args:
        settings: Optional :class:`DatabaseSettings`. If ``None``, loads
            from environment via ``DatabaseSettings()``.

    Returns:
        The initialized SQLAlchemy :class:`~sqlalchemy.engine.Engine`.
    """
    global _engine_factory, _session_factory, _global_settings

    if _engine_factory is not None:
        return _engine_factory.get_engine()

    if settings is None:
        settings = DatabaseSettings()

    _global_settings = settings
    _engine_factory = Genew4EngineFactory(settings)
    _session_factory = db_common.SessionFactory(_engine_factory)

    return _engine_factory.get_engine()


def get_engine() -> Engine:
    """Get the global database engine.

    Returns:
        The SQLAlchemy :class:`~sqlalchemy.engine.Engine` instance.

    Raises:
        db_common.SessionError: If the engine has not been initialized.
    """
    if _engine_factory is None:
        raise SessionError("Database engine not initialized. Call initialize_engine() first.")
    return _engine_factory.get_engine()


def get_settings() -> DatabaseSettings:
    """Get the global database settings.

    Returns:
        The :class:`DatabaseSettings` instance.

    Raises:
        db_common.SessionError: If settings have not been initialized.
    """
    if _global_settings is None:
        raise SessionError("Database settings not initialized. Call initialize_engine() first.")
    return _global_settings


def _require_session_factory() -> db_common.SessionFactory:
    """Return the global SessionFactory, raising SessionError if uninitialized.

    Shared by :func:`get_readwrite_session` and :func:`get_readonly_session`,
    which both need the factory (and both surface the same "engine not
    initialized" error when it is absent).
    """
    if _session_factory is None:
        raise SessionError("Database engine not initialized. Call initialize_engine() first.")
    return _session_factory


@contextmanager
def get_readwrite_session(user: str | None = None) -> Generator[Session, None, None]:
    """Create a session for read-write operations.

    The session is obtained from db-common's
    :meth:`db_common.SessionFactory.get_session`, which commits on clean
    exit and rolls back on exception. This wrapper only populates
    ``session.info`` so audit logging (:mod:`genew4_orm.audit`) can read
    the user / read-only context.

    Args:
        user: Optional user identifier for audit logging. Defaults to
            ``'unknown'``.

    Yields:
        A SQLAlchemy :class:`~sqlalchemy.orm.Session`.

    Example:
        >>> with get_readwrite_session(user="john.doe") as session:
        ...     gene = session.get(Gene, 12345)
        ...     gene.approved_symbol = "NEW"
    """
    session_factory = _require_session_factory()

    with session_factory.get_session() as session:
        session.info["user"] = user if user is not None else "unknown"
        session.info["read_only"] = False
        yield session


@contextmanager
def get_readonly_session() -> Generator[Session, None, None]:
    """Create a read-only session for database queries.

    The session is obtained from db-common's
    :meth:`db_common.SessionFactory.get_readonly_session`, whose
    ``before_commit`` hook raises :class:`ReadOnlySessionError` on any
    commit attempt. This wrapper only populates ``session.info`` so audit
    logging can detect the read-only context.

    Yields:
        A SQLAlchemy :class:`~sqlalchemy.orm.Session` for read-only
        database operations.

    Raises:
        db_common.ReadOnlySessionError: If a commit is attempted.

    Example:
        >>> with get_readonly_session() as session:
        ...     genes = session.execute(select(Gene).limit(10)).scalars().all()
    """
    session_factory = _require_session_factory()

    with session_factory.get_readonly_session() as session:
        session.info["read_only"] = True
        session.info["user"] = None
        yield session


def close_all_sessions() -> None:
    """Close all database sessions and dispose of the engine.

    Resets the module-level ``EngineFactory`` / ``SessionFactory``
    singletons so the next :func:`initialize_engine` call rebuilds them.
    Safe to call when already uninitialized.
    """
    global _engine_factory, _session_factory, _global_settings

    if _session_factory is not None:
        _session_factory.close_all_sessions()

    if _engine_factory is not None:
        _engine_factory.dispose()

    _engine_factory = None
    _session_factory = None
    _global_settings = None


def refresh_engine() -> Engine:
    """Recreate the database engine with the current settings.

    Useful when database configuration has changed and a reconnect with
    new parameters is required.

    Returns:
        The newly created SQLAlchemy :class:`~sqlalchemy.engine.Engine`.

    Raises:
        db_common.SessionError: If no settings are available (engine was
            never initialized).
    """
    if _global_settings is None:
        raise SessionError("Cannot refresh: no settings available.")

    # Capture settings before close_all_sessions clears the singleton.
    settings = _global_settings
    close_all_sessions()
    return initialize_engine(settings)
