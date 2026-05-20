# Testing

This guide covers the test suite for genew4-orm, including running tests, writing new tests, and best practices.

## Test Framework

genew4-orm uses **pytest** as the test framework with the following extensions:

- **pytest-xdist** - Parallel test execution for faster runs
- **pytest-cov** - Code coverage reporting
- **pytest-asyncio** - Async test support (if needed)

## Project Structure

```
tests/
├── unit/
│   ├── test_config.py              # Configuration tests
│   ├── test_models.py              # Model field validation tests
│   ├── test_comment_model.py       # Comment model tests
│   ├── test_gene_has_comment_model.py  # GeneHasComment junction tests
│   ├── test_enums.py               # Enum tests (including PublishStatus)
│   └── test_relationships.py       # Relationship integrity tests
├── integration/
│   ├── test_session.py             # Session management tests
│   ├── test_crud.py                # CRUD operation tests
│   └── test_audit_log.py           # Audit logging tests
└── conftest.py                     # Pytest configuration and fixtures
```

## Running Tests

### Run All Tests

```bash
# Using uv
uv run pytest

# Using pytest directly
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/test_models.py
```

### Run Specific Test

```bash
pytest tests/unit/test_models.py::test_gene_model_fields
```

### Run Tests in Parallel

```bash
# Use all available CPU cores
pytest -n auto

# Use specific number of workers
pytest -n 4
```

### Run with Coverage Report

```bash
# Generate terminal coverage report
pytest --cov=genew4_orm --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=genew4_orm --cov-report=html
open htmlcov/index.html
```

### Run with Verbose Output

```bash
# Show test names and pass/fail status
pytest -v

# Show even more detail (including print statements)
pytest -vv -s
```

## Test Fixtures

### SQLite Session Fixture

For unit tests, use the in-memory SQLite session:

```python
import pytest
from genew4_orm.models import Gene

def test_gene_creation(sqlite_session: SQLAlchemySession) -> None:
    gene = Gene(
        approved_symbol="TEST1",
        approved_name="Test Gene",
        status="Approved",
    )
    sqlite_session.add(gene)
    sqlite_session.commit()

    retrieved = sqlite_session.query(Gene).filter_by(approved_symbol="TEST1").first()
    assert retrieved is not None
    assert retrieved.approved_name == "Test Gene"
```

### Read-Write Session Fixture

For integration tests with PostgreSQL:

```python
@pytest.fixture(scope="function")
def rw_session():
    """Create a read-write session for testing."""
    from genew4_orm.session import initialize_engine, get_readwrite_session

    initialize_engine()

    with get_readwrite_session(user="test_user") as session:
        yield session

    # Cleanup happens automatically via context manager
```

## Writing Tests

### Unit Tests

Test individual models and configurations:

```python
import pytest
from pydantic import ValidationError
from genew4_orm.models import Gene

class TestGeneModel:
    def test_gene_model_fields(self, sqlite_session: SQLAlchemySession) -> None:
        """Test Gene model fields are correctly defined."""
        gene = Gene(
            approved_symbol="BRCA1",
            approved_name="Breast Cancer 1",
            status="Approved",
            locus_type="gene with protein product",
        )
        sqlite_session.add(gene)
        sqlite_session.commit()

        assert gene.id is not None
        assert gene.approved_symbol == "BRCA1"

    def test_gene_status_validation(self) -> None:
        """Test Gene status enum validation."""
        with pytest.raises(ValidationError):
            Gene(approved_symbol="TEST", status="InvalidStatus")
```

### Integration Tests

Test complete workflows:

```python
class TestGeneCRUD:
    def test_create_gene(self, rw_session) -> None:
        """Test creating a gene record."""
        gene = Gene(
            approved_symbol="NEWGENE",
            approved_name="New Gene",
            status="Approved",
        )
        rw_session.add(gene)
        rw_session.commit()

        retrieved = rw_session.get(Gene, gene.id)
        assert retrieved.approved_symbol == "NEWGENE"

    def test_update_gene(self, rw_session) -> None:
        """Test updating a gene record."""
        gene = Gene(
            approved_symbol="TEST",
            approved_name="Original",
            status="Approved",
        )
        rw_session.add(gene)
        rw_session.commit()

        gene.approved_name = "Updated"
        rw_session.commit()

        rw_session.refresh(gene)
        assert gene.approved_name == "Updated"

    def test_delete_gene(self, rw_session) -> None:
        """Test deleting a gene record."""
        gene = Gene(
            approved_symbol="TEST",
            approved_name="Test",
            status="Approved",
        )
        rw_session.add(gene)
        rw_session.commit()

        gene_id = gene.id
        rw_session.delete(gene)
        rw_session.commit()

        retrieved = rw_session.get(Gene, gene_id)
        assert retrieved is None
```

### Relationship Tests

Test model relationships:

```python
class TestGeneRelationships:
    def test_gene_has_groups(self, sqlite_session: SQLAlchemySession) -> None:
        """Test Gene to GeneGroup relationship through junction table."""
        from genew4_orm.models import GeneGroup, GeneHasGeneGroup

        gene = Gene(approved_symbol="TEST", approved_name="Test", status="Approved")
        group = GeneGroup(name="Test Group", abbreviation="TG", status="internal", type="set")

        sqlite_session.add_all([gene, group])
        sqlite_session.commit()

        # Create junction record
        association = GeneHasGeneGroup(
            gene_id=gene.id,
            gene_group_id=group.id,
            sort_order=1,
        )
        sqlite_session.add(association)
        sqlite_session.commit()

        # Verify relationship
        retrieved = sqlite_session.query(GeneHasGeneGroup).filter_by(
            gene_id=gene.id, gene_group_id=group.id
        ).first()
        assert retrieved is not None
```

### Audit Log Tests

Test audit logging functionality:

```python
class TestAuditLogging:
    def test_create_logs_audit_entry(self, rw_session) -> None:
        """Test that CREATE operations are logged."""
        from genew4_orm.models import AuditLog

        gene = Gene(
            approved_symbol="AUDITTEST",
            approved_name="Audit Test",
            status="Approved",
        )
        rw_session.add(gene)
        rw_session.commit()

        # Check audit log was created
        from sqlmodel import select

        statement = select(AuditLog).where(
            AuditLog.entity_type == "Gene",
            AuditLog.entity_id == gene.id,
            AuditLog.operation == "CREATE"
        )
        audit = rw_session.exec(statement).first()
        assert audit is not None
        assert audit.user == "test_user"

    def test_update_logs_audit_entry(self, rw_session) -> None:
        """Test that UPDATE operations are logged."""
        from genew4_orm.models import AuditLog

        gene = Gene(
            approved_symbol="UPDATETEST",
            approved_name="Original",
            status="Approved",
        )
        rw_session.add(gene)
        rw_session.commit()

        gene.approved_name = "Updated"
        rw_session.commit()

        # Check audit log was created
        from sqlmodel import select

        statement = select(AuditLog).where(
            AuditLog.entity_type == "Gene",
            AuditLog.operation == "UPDATE"
        )
        audit = rw_session.exec(statement).first()
        assert audit is not None
        assert "approved_name" in audit.field_changes
```

## Test Organization

### Group Related Tests

Use test classes to group related tests:

```python
class TestGeneModel:
    """Tests for Gene model."""

    def test_fields(self):
        pass

    def test_validation(self):
        pass

class TestGeneGroupModel:
    """Tests for GeneGroup model."""

    def test_fields(self):
        pass

    def test_validation(self):
        pass
```

### Use Descriptive Test Names

Test names should describe what is being tested:

```python
# Good
def test_gene_status_must_be_valid_enum_value(self):
    pass

def test_gene_deletion_cascades_to_associations(self):
    pass

# Bad
def test_gene(self):
    pass

def test_it_works(self):
    pass
```

## Best Practices

1. **Use fixtures** - Leverage pytest fixtures for setup/teardown
2. **Keep tests independent** - Each test should work in isolation
3. **Use descriptive names** - Test names should explain what they test
4. **Test one thing** - Each test should verify a single behavior
5. **Mock external dependencies** - Don't depend on external services in tests
6. **Clean up after tests** - Use fixtures with cleanup logic
7. **Run tests frequently** - Run tests before committing code
8. **Aim for high coverage** - But prioritize critical paths

## Continuous Integration

Tests are run automatically on CI/CD pipelines. The configuration ensures:

- All tests must pass before code can be merged
- Code coverage is tracked
- Linting and type checking must pass

### Pre-commit Requirements

Code cannot be pushed to the remote repository unless:
- All tests pass (`pytest`)
- Linting passes (`ruff check`)
- Type checking passes (`mypy`)

## Test Output Examples

### Successful Test Run

```bash
$ pytest -v

tests/unit/test_config.py::test_database_settings_from_env PASSED
tests/unit/test_models.py::test_gene_model_fields PASSED
tests/unit/test_models.py::test_gene_group_model_fields PASSED
tests/unit/test_relationships.py::test_gene_has_groups PASSED

======================== 116 passed in 2.34s ========================
```

### Failed Test Run

```bash
$ pytest -v

tests/unit/test_models.py::test_gene_model_fields FAILED

======================== FAILURES ========================
____________________ test_gene_model_fields ____________________
    def test_gene_model_fields(self):
>       assert gene.status == "Approved"
E       AssertionError: assert 'Pending' == 'Approved'

======================== 1 failed, 115 passed in 2.12s ========================
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:

```bash
uv pip install -e .
```

### Database Connection Errors

For integration tests, ensure PostgreSQL is running and configured:

```bash
# Check database connection
psql -h localhost -U your_user -d genew4
```

### SQLite Limitations

Some tests may fail with SQLite due to limitations:
- CASCADE deletes work differently
- Type validation may vary
- Foreign key constraints may not be enforced

These are expected and documented in the test suite.
