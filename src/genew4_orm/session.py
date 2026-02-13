"""SQLAlchemy session management and engine factory.

This module provides thread-safe session factories for both read-only
and read-write database operations.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine, event, pool
from sqlalchemy.orm import Session, sessionmaker

from genew4_orm.config.database_settings import DatabaseSettings

_global_engine: Engine | None = None
_global_settings: DatabaseSettings | None = None

# Type alias for sessionmaker factory
SessionMaker = sessionmaker[Session]


class ReadOnlySessionError(Exception):
    """Raised when a write operation is attempted on a read-only session."""

    pass


def _create_engine(settings: DatabaseSettings) -> Engine:
    """Create a SQLAlchemy engine with connection pooling.

    Args:
        settings: DatabaseSettings instance with connection configuration.

    Returns:
        Configured SQLAlchemy Engine instance.
    """
    engine_kwargs = settings.get_engine_kwargs()
    engine_kwargs.update(
        {
            "poolclass": pool.QueuePool,
            "echo": False,  # Set to True for SQL query debugging
        }
    )

    engine = create_engine(
        settings.get_connection_url(with_password=True),
        **engine_kwargs,
    )

    # Register connection pool event listeners for monitoring
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn: Any, connection_record: Any) -> None:
        """Log new database connections."""
        pass  # Could add logging here

    @event.listens_for(engine, "checkout")
    def receive_checkout(
        dbapi_conn: Any, connection_record: Any, connection_proxy: Any
    ) -> None:
        """Log connection checkout from pool."""
        pass  # Could add logging here

    return engine


def initialize_engine(settings: DatabaseSettings | None = None) -> Engine:
    """Initialize the global database engine.

    This should be called once at application startup. If called multiple
    times, the existing engine will be returned.

    Args:
        settings: DatabaseSettings instance. If None, loads from environment.

    Returns:
        The initialized SQLAlchemy Engine.
    """
    global _global_engine, _global_settings

    if _global_engine is not None:
        return _global_engine

    if settings is None:
        settings = DatabaseSettings()

    _global_settings = settings
    _global_engine = _create_engine(settings)

    return _global_engine


def get_engine() -> Engine:
    """Get the global database engine.

    Returns:
        The SQLAlchemy Engine instance.

    Raises:
        RuntimeError: If engine has not been initialized.
    """
    if _global_engine is None:
        raise RuntimeError(
            "Database engine not initialized. Call initialize_engine() first."
        )
    return _global_engine


def get_settings() -> DatabaseSettings:
    """Get the global database settings.

    Returns:
        The DatabaseSettings instance.

    Raises:
        RuntimeError: If settings have not been initialized.
    """
    if _global_settings is None:
        raise RuntimeError(
            "Database settings not initialized. Call initialize_engine() first."
        )
    return _global_settings


# Session maker factories (created after engine initialization)
_session_factory: SessionMaker | None = None
_readonly_session_factory: SessionMaker | None = None


def _get_session_factory() -> SessionMaker:
    """Get or create the standard session factory.

    Returns:
        Session factory for read-write sessions.
    """
    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False
        )

    return _session_factory


def _get_readonly_session_factory() -> SessionMaker:
    """Get or create the read-only session factory.

    Returns:
        Session factory for read-only sessions.
    """
    global _readonly_session_factory

    if _readonly_session_factory is None:
        _readonly_session_factory = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False
        )

    return _readonly_session_factory


@contextmanager
def get_readwrite_session(user: str | None = None) -> Generator[Session, None, None]:
    """Create a session for read-write operations.

    This session allows modifications to the database. All write operations
    will be logged to the audit table.

    Args:
        user: Optional user identifier for audit logging. If not provided,
            defaults to 'unknown'.

    Yields:
        A SQLAlchemy Session for database operations.

    Example:
        >>> with get_readwrite_session(user="john.doe") as session:
        ...     gene = session.get(Gene, 12345)
        ...     gene.approved_symbol = "NEW"
        ...     session.commit()
    """
    if user is None:
        user = "unknown"

    session_factory = _get_session_factory()
    session: Session = session_factory()

    # Store user context in session info for audit logging
    session.info["user"] = user
    session.info["read_only"] = False

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_readonly_session() -> Generator[Session, None, None]:
    """Create a read-only session for database queries.

    This session prevents accidental modifications to the database.
    Any attempt to commit changes will raise a ReadOnlySessionError.

    Yields:
        A SQLAlchemy Session for read-only database operations.

    Example:
        >>> with get_readonly_session() as session:
        ...     genes = session.exec(select(Gene).limit(10)).all()
        ...     for gene in genes:
        ...         print(gene.approved_symbol)

    Raises:
        ReadOnlySessionError: If a commit is attempted on this session.
    """
    session_factory = _get_readonly_session_factory()
    session: Session = session_factory()

    # Mark as read-only for audit logging
    session.info["read_only"] = True
    session.info["user"] = None

    # Hook into before_commit to prevent writes
    @event.listens_for(session, "before_commit")
    def prevent_writes(session: Session) -> None:
        raise ReadOnlySessionError(
            "Cannot commit changes in a read-only session. "
            "Use get_readwrite_session() for modifications."
        )

    try:
        yield session
        # Read-only sessions always rollback, never commit
        session.rollback()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def close_all_sessions() -> None:
    """Close all database sessions and dispose of the engine.

    This should be called before application shutdown to ensure
    clean connection closure.
    """
    global _global_engine, _session_factory, _readonly_session_factory

    if _global_engine is not None:
        _global_engine.dispose()
        _global_engine = None

    _session_factory = None
    _readonly_session_factory = None


def refresh_engine() -> Engine:
    """Recreate the database engine with current settings.

    This is useful when database configuration has changed and
    you need to reconnect with new parameters.

    Returns:
        The newly created SQLAlchemy Engine.
    """
    close_all_sessions()

    if _global_settings is None:
        raise RuntimeError("Cannot refresh: no settings available.")

    return initialize_engine(_global_settings)
