"""Pytest configuration and fixtures for genew4-orm.

This module provides fixtures for testing ORM with both PostgreSQL
and SQLite databases, as well as sample data fixtures.
"""

from collections.abc import Generator

import pytest
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from genew4_orm.config.database_settings import DatabaseSettings
from genew4_orm.models import Gene, GeneGroup, GeneHasGeneGroup
from genew4_orm.session import get_engine

# Test database URLs
TEST_SQLITE_URL = "sqlite:///:memory:"


def _try_postgres_connection() -> bool:
    """Check if PostgreSQL database is available by attempting a connection."""
    settings = DatabaseSettings()

    try:
        # Try to connect to verify database is available
        engine = create_engine(settings.get_connection_url(with_password=True))
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


# PostgreSQL engine fixture for integration tests
@pytest.fixture(scope="session")
def postgres_engine() -> sqlalchemy.engine.Engine:
    """Create a PostgreSQL engine for integration tests.

    This fixture creates an engine that connects to test database.
    Tests using this fixture require a running PostgreSQL instance.

    Yields:
        SQLAlchemy Engine connected to PostgreSQL database.
    """
    # Try to connect to PostgreSQL using DatabaseSettings
    settings = DatabaseSettings()
    if not _try_postgres_connection():
        pytest.skip("PostgreSQL database not available", allow_module_level=True)

    engine = create_engine(
        settings.get_connection_url(with_password=True),
        pool_pre_ping=True,
        echo=False,
    )

    yield engine





# PostgreSQL session fixture
@pytest.fixture(scope="function")
def postgres_session(postgres_engine) -> Generator[Session, None, None]:
    """Create a PostgreSQL session for integration tests.

    Yields:
        SQLAlchemy Session for test database.
    """
    session_local = sessionmaker(bind=postgres_engine, autocommit=False, autoflush=False)
    session = session_local()

    # Set user info for audit logging
    session.info["user"] = "test_user"
    session.info["read_only"] = False

    yield session

    session.close()

    # Cleanup: truncate all tables after test
    with postgres_engine.begin() as conn:
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename NOT LIKE 'pg_%'
            AND tablename NOT LIKE 'sql_%'
        """))
        tables = [row[0] for row in result.fetchall()]
        for table in tables:
            conn.execute(text(f'TRUNCATE TABLE public."{table}" CASCADE'))


# SQLite engine fixture for unit tests
@pytest.fixture(scope="function")
def sqlite_unit_engine():
    """Create an in-memory SQLite engine for unit tests.

    This fixture is useful for fast unit tests that don't require
    full PostgreSQL compatibility.

    Yields:
        SQLAlchemy Engine connected to in-memory SQLite database.
    """
    engine = create_engine(
        TEST_SQLITE_URL,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    from genew4_orm import models  # noqa: F401

    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


# SQLite session fixture
@pytest.fixture(scope="function")
def sqlite_session(sqlite_unit_engine) -> Generator[Session, None, None]:
    """Create an SQLite session for unit tests.

    Yields:
        SQLAlchemy Session for in-memory SQLite database.
    """
    session_local = sessionmaker(bind=sqlite_unit_engine, autocommit=False, autoflush=False)
    session = session_local()

    # Set user info for audit logging
    session.info["user"] = "test_user"
    session.info["read_only"] = False

    yield session

    session.close()


# Sample data fixtures


@pytest.fixture
def sample_gene() -> Gene:
    """Create a sample Gene object for testing.

    Returns:
        Gene object with sample data.
    """
    return Gene(
        id=12345,
        approved_symbol="TEST1",
        approved_name="Test Gene 1",
        locus_type="GWPP",
        status="Approved",
        chromosomal_location="chr1",
        public_ncbi_gene_id=12345,
        editor="test_curator",
    )


@pytest.fixture
def sample_gene_group() -> GeneGroup:
    """Create a sample GeneGroup object for testing.

    Returns:
        GeneGroup object with sample data.
    """
    return GeneGroup(
        name="Test Gene Group",
        abbreviation="TGG",
        editor="test_curator",
        status="exported",
        type="set",
    )


@pytest.fixture
def sample_gene_with_group(sample_gene, sample_gene_group) -> tuple[Gene, GeneGroup, GeneHasGeneGroup]:
    """Create a sample Gene associated with a GeneGroup.

    Args:
        sample_gene: Gene fixture.
        sample_gene_group: GeneGroup fixture.

    Returns:
        Tuple of (Gene, GeneGroup, GeneHasGeneGroup).
    """
    gene_group_has_gene = GeneHasGeneGroup(
        gene_id=sample_gene.id,
        gene_group_id=sample_gene_group.id,
        sort_order=1,
    )
    return sample_gene, sample_gene_group, gene_group_has_gene


# Unified test session fixture - uses PostgreSQL if available, else SQLite
@pytest.fixture(scope="function")
def test_session(sqlite_unit_engine):
    """Create a test session that works with either PostgreSQL or SQLite.

    This fixture uses PostgreSQL if available, otherwise falls back to SQLite.
    This allows PostgreSQL-specific tests to run when PostgreSQL is available,
    while still allowing other tests to work with SQLite.

    Yields:
        SQLAlchemy Session configured for test database.
    """
    if _try_postgres_connection():
        # PostgreSQL available - use postgres_session fixture
        session_local = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
        session = session_local()

        # Set user info for audit logging
        session.info["user"] = "test_user"
        session.info["read_only"] = False

        yield session

        session.close()
    else:
        # PostgreSQL not available - use SQLite
        yield sqlite_session(sqlite_unit_engine)


# Alembic migration fixtures
