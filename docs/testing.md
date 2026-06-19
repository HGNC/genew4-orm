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
├── unit/                         # Fast, isolated unit tests (in-memory SQLite)
│   ├── conftest fixtures use sqlite_session
│   ├── test_config.py            # Configuration / DatabaseSettings
│   ├── test_enums.py             # Enum definitions
│   ├── test_audit_log_model.py   # AuditLog model + (de)serialization helpers
│   ├── test_audit.py             # Audit event listener behaviour
│   ├── test_*_model.py           # Per-model field/relationship tests
│   ├── test_junction_models.py   # Junction-table models
│   ├── test_phase2_models.py     # Phase 2 cross-reference / sequence models
│   └── test_query_helpers.py     # Query helper functions
├── integration/                  # Cross-model workflows (SQLite, + PostgreSQL)
│   ├── test_audit_logging.py
│   ├── test_readonly_session.py
│   ├── test_user.py, test_editor.py, test_specialist.py, ...
│   └── postgresql/               # PostgreSQL-specific integration tests
│       ├── test_gene_crud.py
│       ├── test_schema_validation.py
│       └── test_postgresql_types.py
├── session/                      # Session lifecycle / engine / settings tests
│   ├── test_session_module.py
│   └── test_session_lifecycle.py
├── e2e/                          # End-to-end workflows against a real DB
│   ├── test_gene_lifecycle.py
│   ├── test_audit_trail_workflows.py
│   └── test_data_integrity.py
├── utils/                        # Tests for utility modules
│   └── test_query_helpers.py
└── conftest.py                   # Shared pytest fixtures (engines / sessions)
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
pytest tests/unit/test_user_model.py
```

### Run Specific Test

```bash
pytest tests/unit/test_user_model.py::test_user_model
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

Shared fixtures live in `tests/conftest.py` (and `tests/e2e/conftest.py`).

### SQLite Session Fixture

For unit tests, use the in-memory `sqlite_session` fixture. It already seeds
`session.info` (`user`, `read_only`) so audit logging behaves the same as in
production:

```python
from sqlalchemy import select
from genew4_orm.models import Gene


def test_gene_creation(sqlite_session) -> None:
    gene = Gene(
        hgnc_id=1100,
        approved_symbol="TEST1",
        approved_name="Test Gene",
        status="Approved",
    )
    sqlite_session.add(gene)
    sqlite_session.commit()

    retrieved = sqlite_session.scalars(
        select(Gene).where(Gene.approved_symbol == "TEST1")
    ).first()
    assert retrieved is not None
    assert retrieved.approved_name == "Test Gene"
```

### PostgreSQL Session Fixture

For integration tests against PostgreSQL, `conftest.py` provides a
`postgres_session` fixture (function-scoped) and an `e2e_session` fixture for
end-to-end tests. A PostgreSQL service must be available — see the
[Development Workflow](development-workflow.md) for starting one with
`docker-compose`.

## Writing Tests

### Unit Tests

Test individual models and configurations:

```python
from genew4_orm.models import Gene


class TestGeneModel:
    def test_gene_model_fields(self, sqlite_session) -> None:
        """Test Gene model fields are correctly defined."""
        gene = Gene(
            hgnc_id=1100,
            approved_symbol="BRCA1",
            approved_name="Breast Cancer 1",
            status="Approved",
            locus_type="gene with protein product",
        )
        sqlite_session.add(gene)
        sqlite_session.commit()

        assert gene.hgnc_id == 1100
        assert gene.approved_symbol == "BRCA1"

    def test_gene_status_default(self) -> None:
        """status defaults to 'Pending' when not provided."""
        gene = Gene(hgnc_id=1101, approved_symbol="TEST")
        # The column-level default is applied on flush; at construction the
        # value is unset, so persist it to check the default.
        assert gene.status is None or gene.status == "Pending"
```

> Models are plain SQLAlchemy 2.0 declarative classes (not Pydantic models), so
> constructing one with an arbitrary string does **not** raise a validation
> error. Validate domain values explicitly in your tests, e.g.
> `assert value in {s.value for s in GeneStatus}`.

### Integration Tests

Test complete workflows:

```python
class TestGeneCRUD:
    def test_create_gene(self, sqlite_session) -> None:
        """Test creating a gene record."""
        gene = Gene(
            hgnc_id=1100,
            approved_symbol="NEWGENE",
            approved_name="New Gene",
            status="Approved",
        )
        sqlite_session.add(gene)
        sqlite_session.commit()

        retrieved = sqlite_session.get(Gene, gene.hgnc_id)
        assert retrieved.approved_symbol == "NEWGENE"

    def test_update_gene(self, sqlite_session) -> None:
        """Test updating a gene record."""
        gene = Gene(hgnc_id=1100, approved_symbol="TEST", approved_name="Original", status="Approved")
        sqlite_session.add(gene)
        sqlite_session.commit()

        gene.approved_name = "Updated"
        sqlite_session.commit()

        sqlite_session.refresh(gene)
        assert gene.approved_name == "Updated"

    def test_delete_gene(self, sqlite_session) -> None:
        """Test deleting a gene record."""
        gene = Gene(hgnc_id=1100, approved_symbol="TEST", approved_name="Test", status="Approved")
        sqlite_session.add(gene)
        sqlite_session.commit()

        gene_id = gene.hgnc_id
        sqlite_session.delete(gene)
        sqlite_session.commit()

        retrieved = sqlite_session.get(Gene, gene_id)
        assert retrieved is None
```

### Relationship Tests

Test model relationships:

```python
from sqlalchemy import select

from genew4_orm.models import GeneGroup, GeneHasGeneGroup


class TestGeneRelationships:
    def test_gene_has_groups(self, sqlite_session) -> None:
        """Test Gene to GeneGroup relationship through the junction table."""
        gene = Gene(hgnc_id=1100, approved_symbol="TEST", approved_name="Test", status="Approved")
        group = GeneGroup(name="Test Group", abbreviation="TG")

        sqlite_session.add_all([gene, group])
        sqlite_session.commit()

        # Create junction record
        association = GeneHasGeneGroup(
            gene_id=gene.hgnc_id,
            gene_group_id=group.id,
            custom_sort="A",
        )
        sqlite_session.add(association)
        sqlite_session.commit()

        # Verify relationship
        retrieved = sqlite_session.scalars(
            select(GeneHasGeneGroup).where(
                GeneHasGeneGroup.gene_id == gene.hgnc_id,
                GeneHasGeneGroup.gene_group_id == group.id,
            )
        ).first()
        assert retrieved is not None
```

### Audit Log Tests

Test audit logging functionality. Remember that `field_changes` is persisted as
a JSON **string**, so parse it with `json.loads()` when asserting on it:

```python
import json

from sqlalchemy import select

from genew4_orm.models import AuditLog, Gene


class TestAuditLogging:
    def test_create_logs_audit_entry(self, sqlite_session) -> None:
        """Test that CREATE operations are logged."""
        gene = Gene(
            hgnc_id=1100,
            approved_symbol="AUDITTEST",
            approved_name="Audit Test",
            status="Approved",
        )
        sqlite_session.add(gene)
        sqlite_session.commit()

        statement = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == "Gene",
                AuditLog.operation == "CREATE",
            )
        )
        audit = sqlite_session.scalars(statement).first()
        assert audit is not None
        assert audit.user == "test_user"  # set by the sqlite_session fixture

    def test_update_logs_field_change(self, sqlite_session) -> None:
        """Test that UPDATE operations record the changed field."""
        gene = Gene(hgnc_id=1100, approved_symbol="UPDATETEST", approved_name="Original", status="Approved")
        sqlite_session.add(gene)
        sqlite_session.commit()

        gene.approved_name = "Updated"
        sqlite_session.commit()

        statement = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == "Gene",
                AuditLog.operation == "UPDATE",
            )
        )
        audit = sqlite_session.scalars(statement).first()
        assert audit is not None
        changes = json.loads(audit.field_changes)
        assert "approved_name" in changes
```

## Test Organization

### Group Related Tests

Use test classes to group related tests:

```python
class TestGeneModel:
    """Tests for Gene model."""

    def test_fields(self):
        pass

    def test_defaults(self):
        pass


class TestGeneGroupModel:
    """Tests for GeneGroup model."""

    def test_fields(self):
        pass
```

### Use Descriptive Test Names

Test names should describe what is being tested:

```python
# Good
def test_gene_status_must_be_a_known_status_value():
    pass

def test_gene_deletion_cascades_to_associations():
    pass

# Bad
def test_gene():
    pass

def test_it_works():
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
tests/unit/test_user_model.py::test_user_model PASSED
tests/unit/test_gene_group_model.py::test_gene_group_model PASSED
tests/unit/test_junction_models.py::test_gene_has_gene_group PASSED

======================== 116 passed in 2.34s ========================
```

### Failed Test Run

```bash
$ pytest -v

tests/unit/test_user_model.py::test_user_model FAILED

======================== FAILURES ========================
____________________ test_user_model ____________________
    def test_user_model():
>       assert user.email == "expected@example.com"
E       AssertionError: assert 'other@example.com' == 'expected@example.com'

======================== 1 failed, 115 passed in 2.12s ========================
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed (editable) and on the
path:

```bash
uv pip install -e .
```

The test suite adds `src` to `sys.path` via `pyproject.toml`
(`tool.pytest.pythonpath = ["src"]`).

### Database Connection Errors

For PostgreSQL integration tests, ensure PostgreSQL is running and configured:

```bash
# Check database connection
psql -h localhost -U your_user -d genew4
```

### SQLite Limitations

Some tests may behave differently with SQLite compared to PostgreSQL:

- Enum constraints and native types are not enforced the same way
- Foreign-key / cascade behaviour can differ
- PostgreSQL-specific columns (e.g. sequences) have no SQLite equivalent

The dedicated `tests/integration/postgresql/` suite covers the cases that require
a real PostgreSQL instance.
