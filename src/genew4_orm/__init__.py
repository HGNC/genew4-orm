"""genew4-orm: Python ORM for the genew4 PostgreSQL database.

This package provides a type-safe, validated interface for accessing
the genew4 database with built-in audit logging and connection pooling.

Audit logging is enabled automatically when the package is imported: importing
``genew4_orm`` attaches the audit ``before_flush`` listener to the SQLAlchemy
``Session`` (see the side-effect ``import genew4_orm.audit`` below), so all write
operations are tracked without any explicit setup.
"""

# Side-effect import: attaching the audit `before_flush` listener is a module-import
# side effect of `genew4_orm.audit` (via `@event.listens_for(Session, ...)`). Importing
# it here makes audit logging active by default the moment the package is imported,
# rather than only when something explicitly imports `genew4_orm.audit`.
import genew4_orm.audit  # noqa: F401
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
