"""Pytest fixtures for end-to-end tests.

This module provides fixtures specifically designed for E2E testing,
focusing on test isolation and automatic cleanup.
"""

from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

# Import audit module to register event listeners
# This ensures audit logging works for E2E tests
import genew4_orm.audit  # noqa: F401
from genew4_orm.models import Gene, GeneGroup
from genew4_orm.session import (
    get_engine,
    initialize_engine,
)


@pytest.fixture(scope="function")
def e2e_session() -> Generator[SQLAlchemySession, None]:
    """Create an E2E test session with automatic transaction cleanup.

    Unlike integration tests which test individual operations,
    E2E tests create complex state that needs full isolation.
    Each test gets a fresh session and all changes are rolled back.

    Yields:
        SQLAlchemySession configured for E2E testing.
        None: No teardown needed (automatic rollback).
    """
    # Initialize engine first (required before get_engine)
    initialize_engine()

    engine = get_engine()
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Begin transaction for test isolation
    connection = engine.connect()
    session = session_local(bind=connection)

    # Set user context for audit logging
    session.info["user"] = "e2e_test_user"
    session.info["read_only"] = False

    yield session

    # Teardown: ALWAYS rollback to maintain database state
    session.rollback()
    connection.close()


@pytest.fixture(scope="function")
def gene_factory() -> Generator:
    """Factory for creating unique genes in E2E tests.

    Uses a counter to ensure each gene gets a unique symbol,
    preventing conflicts when tests run multiple times or in parallel.

    Yields:
        Callable that creates Gene objects with unique symbols.
    """
    counter = 0

    def create(**kwargs):
        nonlocal counter
        counter += 1
        default_kwargs = {
            "approved_symbol": f"E2E_GENE_{counter}",
            "approved_name": f"E2E Test Gene {counter}",
            "status": "Pending",
        }
        default_kwargs.update(kwargs)
        return Gene(**default_kwargs)

    return create


@pytest.fixture(scope="function")
def gene_group_factory() -> Generator:
    """Factory for creating unique gene groups in E2E tests.

    Uses a counter to ensure each group gets a unique name,
    preventing conflicts when tests run multiple times or in parallel.

    Yields:
        Callable that creates GeneGroup objects with unique names.
    """
    counter = 0

    def create(**kwargs):
        nonlocal counter
        counter += 1
        default_kwargs = {
            "name": f"E2E_Group_{counter}",
            "status": "exported",
        }
        default_kwargs.update(kwargs)
        return GeneGroup(**default_kwargs)

    return create
