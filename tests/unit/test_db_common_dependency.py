"""Regression guard for the db-common dependency (Task T1).

The module-level imports below are themselves the importability test: if
db-common cannot be resolved from its pinned git source, or any required symbol
is gone, collection fails with ModuleNotFoundError/ImportError — the exact RED
state the T1 verify line guards against. The single test additionally pins these
symbols to db_common.__all__ so a silent privatization fails here, not in a
later migration task.
"""

import db_common
from db_common import (  # noqa: F401 - imported to prove importability at collection time
    DatabaseDriver,
    DatabaseSettings,
    DeclarativeBase,
    EngineFactory,
    ReadOnlySessionError,
    SessionError,
    SessionFactory,
)

# Symbols the migration (T2-T5) delegates to.
EXPECTED_PUBLIC_SYMBOLS = {
    "DatabaseSettings",
    "DatabaseDriver",
    "EngineFactory",
    "SessionFactory",
    "DeclarativeBase",
    "SessionError",
    "ReadOnlySessionError",
}


def test_db_common_keeps_required_symbols_public() -> None:
    """All migration-critical symbols remain declared in db_common.__all__."""
    missing = EXPECTED_PUBLIC_SYMBOLS - set(db_common.__all__)
    assert not missing, f"db_common no longer exports: {sorted(missing)}"
