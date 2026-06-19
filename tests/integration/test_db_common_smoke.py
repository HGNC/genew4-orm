"""End-to-end smoke test proving genew4-orm runs on db-common end to end.

Verifies the migration's end state against a real in-memory SQLite database
(no mocks on db-common): the migrated session path (``initialize_engine`` +
``get_readwrite_session`` + ``get_readonly_session``) round-trips a
``Gene``/``AuditLog`` insert through db-common's ``EngineFactory`` /
``SessionFactory``, and alembic's ``target_metadata`` is the shared
``db_common.DeclarativeBase.metadata`` registry that holds every genew4 table.
"""

import ast
from pathlib import Path

import pytest
from db_common import DeclarativeBase

from genew4_orm.config.database_settings import Genew4DatabaseSettings
from genew4_orm.models import Gene
from genew4_orm.models.audit_log import AuditLog
from genew4_orm.session import (
    ReadOnlySessionError,
    close_all_sessions,
    get_readonly_session,
    get_readwrite_session,
    initialize_engine,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_ENV = REPO_ROOT / "alembic" / "env.py"


@pytest.fixture
def sqlite_engine():
    """Bind the migrated session path to an in-memory SQLite database.

    ``Genew4DatabaseSettings(driver="sqlite")`` lets db-common's ``get_url()``
    return ``sqlite:///:memory:`` and ``Genew4EngineFactory`` provision a
    ``StaticPool``. Tables are created from ``db_common.DeclarativeBase.metadata``
    (the shared registry), proving the metadata source was swapped correctly.
    """
    close_all_sessions()
    settings = Genew4DatabaseSettings(driver="sqlite")
    engine = initialize_engine(settings)
    DeclarativeBase.metadata.create_all(engine)
    try:
        yield engine
    finally:
        DeclarativeBase.metadata.drop_all(engine)
        close_all_sessions()


def _alembic_target_metadata_rhs() -> str:
    """Return the source text of alembic/env.py's ``target_metadata = <expr>``."""
    tree = ast.parse(ALEMBIC_ENV.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "target_metadata":
                    return ast.unparse(node.value)
    pytest.fail("alembic/env.py does not assign target_metadata")


def test_alembic_target_metadata_is_db_common_registry() -> None:
    """alembic autogenerate must target ``db_common.DeclarativeBase.metadata``."""
    rhs = _alembic_target_metadata_rhs()
    assert rhs == "DeclarativeBase.metadata", f"alembic target_metadata should be DeclarativeBase.metadata, got {rhs!r}"
    # Confirm the expression resolves to the actual shared registry object.
    resolved = eval(  # noqa: S307 - controlled AST-derived string from our own env.py
        compile(rhs, str(ALEMBIC_ENV), "eval"), {"DeclarativeBase": DeclarativeBase}
    )
    assert resolved is DeclarativeBase.metadata


def test_db_common_registry_holds_genew4_tables() -> None:
    """``DeclarativeBase.metadata`` is the shared registry with every genew4 table."""
    table_names = set(DeclarativeBase.metadata.tables)
    # Spot-check a representative slice spanning the FK graph.
    expected = {
        "hgnc",
        "family_new",
        "user",
        "reminder",
        "audit_log",
        "comment",
        "gene_has_comment",
        "gene_has_family",
        "editor",
    }
    assert expected <= table_names


def test_readwrite_session_round_trips_gene_and_audit(sqlite_engine) -> None:
    """``get_readwrite_session()`` inserts + commits Gene/AuditLog via db-common.

    The AuditLog assertion isolates *our* row by its unique ``field_changes``
    content rather than by row count: ``genew4_orm.audit``'s ``before_flush``
    listener attaches globally once any test imports it, and — when attached —
    also writes AuditLog rows for these inserts (a pre-existing quirk this
    migration deliberately does not change). Querying by our exact payload
    stays green whether or not that listener is active.
    """
    audit_payload = {"symbol": {"old": None, "new": "SMOKE"}}
    with get_readwrite_session(user="alice") as session:
        session.add(
            Gene(
                hgnc_id=42,
                approved_symbol="SMOKE",
                approved_name="smoke gene",
                locus_type="gene with protein product",
                status="Approved",
                chromosomal_location="chr1",
                public_ncbi_gene_id=1,
                editor="curator",
            )
        )
        # field_changes is a real dict on the model: AuditLog.field_changes uses a
        # JSONEncodedDict TypeDecorator that serializes to JSON text on write, so we
        # pass the dict directly (mirroring audit_write_operations' usage).
        session.add(
            AuditLog(
                user="alice",
                operation="CREATE",
                entity_type="Gene",
                entity_id=42,
                field_changes=audit_payload,
            )
        )

    with get_readonly_session() as session:
        fetched = session.get(Gene, 42)
        assert fetched is not None
        assert fetched.approved_symbol == "SMOKE"
        mine = session.query(AuditLog).filter(AuditLog.field_changes == audit_payload).one()
        assert mine.user == "alice"
        assert mine.operation == "CREATE"


def test_readonly_session_rejects_commit(sqlite_engine) -> None:
    """``get_readonly_session()`` delegates read-only enforcement to db-common."""
    with pytest.raises(ReadOnlySessionError):
        with get_readonly_session() as session:
            session.commit()
