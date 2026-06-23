"""Regression guard for the db-common dependency (Task T1 + T6).

The module-level imports below are themselves the importability test: if
db-common cannot be resolved from its pinned git source, or any required symbol
is gone, collection fails with ModuleNotFoundError/ImportError — the exact RED
state the T1 verify line guards against. The symbol-membership test pins these
to db_common.__all__ so a silent privatization fails here, not in a later
migration task.

The T6 tests additionally guard the v0.2.0 pin: the installed db-common must be
>=0.2.0 (the charset behavior change + py.typed typing change both landed in
0.2.0) and must ship the py.typed marker so its real types flow through to
genew4-orm under ``strict = true`` mypy.
"""

import importlib.metadata as metadata
import os

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


class TestDbCommonV02Pin:
    """Guard the v0.2.0 dependency pin (Task T6).

    genew4-orm (Postgres) gains no runtime behavior from the v0.2.0 bump — the
    MySQL-only ``SET NAMES utf8mb4`` listener never fires for the ``postgresql``
    driver. The bump exists to consume db-common's now-shipped ``py.typed``
    marker so its real types flow through to this repo's ``strict = true``
    mypy. These two tests are the RED gate for that bump: before the pin moves
    off ``v0.1.0`` the installed version is ``0.1.0`` and ``py.typed`` is absent.
    """

    def test_db_common_version_at_least_0_2_0(self) -> None:
        """The resolved/installed db-common is >=0.2.0.

        Version is compared as a parsed tuple rather than via ``packaging`` to
        avoid depending on that package transitively (it is not declared in
        genew4-orm's ``dependencies`` / ``dev`` group).
        """
        version = metadata.version("db-common")
        parsed = tuple(int(part) for part in version.split("."))
        assert parsed >= (0, 2, 0), f"db-common {version} is pinned below 0.2.0; bump the pin + regenerate uv.lock"

    def test_db_common_ships_py_typed_marker(self) -> None:
        """The installed db-common ships py.typed (so its types are real, not Any).

        db-common only began shipping py.typed in 0.2.0; its absence means every
        db-common symbol is ``Any`` under mypy, which is exactly the state
        genew4's ``disallow_subclassing_any = false`` /
        ``db_common.*`` ``ignore_missing_imports`` override exists to paper over.
        """
        package_dir = os.path.dirname(db_common.__file__)
        assert package_dir, "db_common.__file__ resolved without a directory"

        marker = os.path.join(package_dir, "py.typed")
        assert os.path.exists(marker), (
            f"db-common at {package_dir} ships no py.typed; the v0.2.0 pin has "
            "not resolved (it should pull in the typed package)"
        )
