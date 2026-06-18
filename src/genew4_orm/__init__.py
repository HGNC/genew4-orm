"""genew4-orm: Python ORM for the genew4 PostgreSQL database.

This package provides a type-safe, validated interface for accessing
the genew4 database with built-in audit logging and connection pooling.
"""

from genew4_orm.config.database_settings import DatabaseSettings
from genew4_orm.session import (
    ReadOnlySessionError,
    SessionError,
    close_all_sessions,
    get_engine,
    get_readonly_session,
    get_readwrite_session,
    initialize_engine,
    refresh_engine,
)

__all__ = [
    "DatabaseSettings",
    "ReadOnlySessionError",
    "SessionError",
    "initialize_engine",
    "get_engine",
    "get_readonly_session",
    "get_readwrite_session",
    "close_all_sessions",
    "refresh_engine",
]

__version__ = "0.1.0"
