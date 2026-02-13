# Product Requirements Document: genew4-orm

## 1. Project Overview

### 1.1 Purpose

Create a Python 3 ORM for the PostgreSQL database `genew4`, providing a typed, validated interface for internal tools. The ORM will be based on the existing TypeScript/TypeORM implementation in `hgnc-tools-api` to ensure schema compatibility and feature parity.

### 1.2 Target Users

Internal team members (8 people) who need programmatic access to the genew4 database for data management, analysis, and tooling.

### 1.3 Success Criteria

* All 13 database entities implemented with full type safety
* Read-only operations work by default (safe mode)
* Full CRUD operations available when explicitly enabled
* Comprehensive test coverage (unit + integration)
* Professional documentation via MkDocs
* Installable package via uv/pip

## 2. Technical Architecture

### 2.1 Core Technology Stack

**ORM Framework**: SQLModel 0.0.14+

* Combines SQLAlchemy 2.0 + Pydantic for type-safe models
* Native support for PostgreSQL features
* Excellent validation and serialization

**Database Driver**: psycopg3 (synchronous)

* PostgreSQL-specific driver
* Better performance than psycopg2
* Synchronous execution model

**Python Version**: 3.11+

* Modern type hints support
* Better performance
* Required for latest Pydantic features

**Package Management**: UV

* Fast dependency resolution
* Reproducible builds
* Team standard

### 2.2 Project Structure

```text
genew4-orm/
├── src/
│   └── genew4_orm/
│       ├── __init__.py
│       ├── config.py              # Pydantic settings
│       ├── session.py             # Session factories
│       ├── enums.py               # All enum definitions
│       ├── audit.py               # Audit logging
│       ├── models/
│       │   ├── __init__.py
│       │   ├── gene.py
│       │   ├── gene_group.py
│       │   ├── gene_has_gene_group.py
│       │   ├── gene_group_alias.py
│       │   ├── hierarchy_closure.py
│       │   ├── specialist.py
│       │   ├── external_resource.py
│       │   ├── correspondence.py
│       │   ├── user.py
│       │   ├── editor.py
│       │   ├── reminder.py
│       │   ├── grch38_mapping.py
│       │   ├── cytoband.py
│       │   └── audit_log.py       # Audit trail table
│       └── utils/
│           ├── __init__.py
│           └── query_helpers.py   # Eager loading utilities
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/                      # SQLite-based fast tests
│   │   ├── test_models.py
│   │   ├── test_relationships.py
│   │   └── test_validation.py
│   └── integration/               # PostgreSQL-based tests
│       ├── test_crud_operations.py
│       ├── test_schema_validation.py
│       ├── test_audit_logging.py
│       └── test_query_performance.py
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py  # From existing DB
│   └── env.py
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── configuration.md
│   ├── models.md
│   ├── querying.md
│   ├── crud-operations.md
│   ├── audit-logging.md
│   └── testing.md
├── mkdocs.yml
├── pyproject.toml
├── README.md
└── WARP.md
```

### 2.3 Database Entities

All 13 entities from the TypeScript ORM:

**Core Gene Data**

1. **Gene** (`hgnc` table) - Primary gene entity with 40+ fields including enums, dates, external IDs
2. **GeneGroup** (`family_new` table) - Gene family/group management
3. **GeneHasGeneGroup** (`gene_has_family` table) - Many-to-many junction with custom sort
4. **GeneGroupAlias** (`family_alias` table) - Alternative names for gene groups
5. **HierarchyClosure** (`hierarchy_closure` table) - Transitive closure for hierarchical relationships

**Reference Data**

6. **Specialist** (`specialist` table) - External specialist organizations
7. **ExternalResource** (`external_resource` table) - External database links
8. **Correspondence** (`corr` table) - Communication records
9. **Editor** (`editor` table) - Legacy editor users
10. **User** (`user` table) - Modern authentication users
11. **Reminder** (`reminder` table) - User task reminders

**Genomic Mapping**

12. **Grch38Mapping** (`coord_match_grch38` table) - GRCh38 coordinate mappings
13. **Cytoband** (`cytoband` table) - Cytogenetic band data

**Audit Trail**

14. **AuditLog** (`audit_log` table) - Write operation tracking (new table)

### 2.4 Type Safety

**Enums**

* All TypeScript enums converted to Python str-based Enums
* `GeneLocusType` (38 values)
* `GeneStatus` (8 values)
* `GeneGroupStatus` (3 values)
* `GeneGroupType` (1 value currently)
* `Grch38SourceType` (4 values)
* `Grch38MarkType` (2 values)
* `CytobandSourceType` (2 values)

**Date/DateTime Handling**

* Use Python `date` objects for date fields
* Use Python `datetime` objects for timestamp fields
* Automatic serialization to/from PostgreSQL date types
* Validation ensures proper formats

**Nullable Fields**

* Explicit `Optional[T]` or `T | None` for all nullable database columns
* Match TypeScript nullable: true fields exactly

### 2.5 Relationships

Mirror TypeScript ORM relationships:

* **One-to-Many**: Gene → GeneHasGeneGroup, GeneGroup → GeneGroupAlias, User → Reminder
* **Many-to-Many**: Gene ↔ GeneGroup (via GeneHasGeneGroup), GeneGroup ↔ Specialist, GeneGroup ↔ ExternalResource, GeneGroup ↔ Correspondence
* **Self-Referential**: GeneGroup parents/children with hierarchy closure table
* **Cascade Behavior**: Mirror `orphanedRowAction: 'delete'` using SQLAlchemy cascade options

## 3. Access Control & Session Management

### 3.1 Read-Only by Default

**Default Session Factory**

```python
from genew4_orm import get_readonly_session
from genew4_orm.models import Gene
from sqlmodel import select

with get_readonly_session() as session:
    genes = session.exec(select(Gene)).all()
    # Read operations work normally
    
    # Writes will raise error on commit attempt
    gene = genes[0]
    gene.approved_symbol = "NEW"  # Modification allowed
    session.commit()  # Raises ReadOnlySessionError
```

**Implementation**

* Read-only session uses transaction with rollback-only mode
* Clear error messages when write attempted
* Prevents accidental data modification

### 3.2 Read-Write Sessions

**Explicit Write Session Factory**

```python
from genew4_orm import get_readwrite_session
from genew4_orm.models import Gene

with get_readwrite_session(user="john.doe") as session:
    gene = session.get(Gene, 12345)
    gene.approved_symbol = "NEW"
    session.commit()  # Succeeds, audit log created
```

**Requirements**

* User identifier required for all write sessions
* Raises error if user not provided
* All write operations automatically audited

### 3.3 User Context

**Default Behavior**

* User passed to `get_readwrite_session(user="username")`
* Stored in session info for audit logging
* Validated (non-empty string)

**Future Enhancement**

* Could integrate with authentication system
* Could use system username if not provided
* Could support user objects with more metadata

## 4. Audit Logging

### 4.1 Audit Requirements

**What to Log**

* Write operations only (CREATE, UPDATE, DELETE)
* Field-level changes (old value → new value)
* User performing operation
* Timestamp of operation
* Entity type and ID

**What NOT to Log**

* Read operations (too verbose, performance impact)
* Password fields or sensitive data
* Large binary/text fields (email bodies)

### 4.2 Audit Schema

```python
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user: str = Field(max_length=100)
    operation: str = Field(max_length=10)  # CREATE, UPDATE, DELETE
    entity_type: str = Field(max_length=100)  # "Gene", "GeneGroup", etc.
    entity_id: int
    field_changes: dict = Field(sa_column=Column(JSON))
```

**Field Changes JSON Structure**

```json
{
  "approved_symbol": {"old": "BRCA1", "new": "BRCA1P1"},
  "status": {"old": "Approved", "new": "Symbol Withdrawn"}
}
```

For CREATE operations, old values are null. For DELETE operations, new values are null.

### 4.3 Implementation

* SQLAlchemy event listeners on session flush
* Automatic comparison of dirty objects
* Transactional consistency (audit + change atomic)
* Exclude fields: passwords, jwt tokens, lock fields

## 5. Configuration

### 5.1 Database Configuration

**Pydantic Settings**

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    pg_host: str
    pg_port: int = 5432
    pg_name: str
    pg_user: str
    pg_password: SecretStr
    
    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
```

**Environment Variables**

```bash
PG_HOST=localhost
PG_PORT=5432
PG_NAME=genew4
PG_USER=genew_user
PG_PASSWORD=secret
```

### 5.2 Connection Management

* Connection pooling enabled by default
* Pool size: 5 connections (sufficient for 8-person team)
* Max overflow: 10 (handles spikes)
* Pool recycle: 1 hour (prevent stale connections)
* Configurable via environment or settings override

## 6. Performance Optimization

### 6.1 Eager Loading Helpers

**Query Helpers Module**

```python
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload, joinedload

def get_gene_with_groups(session: Session, gene_id: int) -> Gene | None:
    """Get gene with gene groups eagerly loaded."""
    stmt = select(Gene).where(Gene.id == gene_id).options(
        selectinload(Gene.gene_has_gene_groups).selectinload(GeneHasGeneGroup.gene_group)
    )
    return session.exec(stmt).first()

def get_gene_group_with_hierarchy(session: Session, group_id: int) -> GeneGroup | None:
    """Get gene group with parent/child relationships loaded."""
    stmt = select(GeneGroup).where(GeneGroup.id == group_id).options(
        selectinload(GeneGroup.parents),
        selectinload(GeneGroup.children)
    )
    return session.exec(stmt).first()
```

**Common Pre-Optimized Queries**

* Gene with gene groups
* Gene group with hierarchy (parents/children)
* Gene group with specialists and external resources
* User with reminders

### 6.2 Query Best Practices Documentation

* When to use `selectinload` vs `joinedload`
* Avoiding N+1 queries
* Bulk operations for multiple records
* Example patterns for common use cases

### 6.3 No Caching Initially

* All queries hit database (data freshness guaranteed)
* Can add application-level caching later if needed
* Reference data (specialists, external resources) good candidates for future caching

## 7. Testing Strategy

### 7.1 Test Infrastructure

**Hybrid Approach**

* **Unit Tests**: SQLite in-memory for fast feedback
    * Model validation
    * Relationship definitions
    * Enum values
    * Basic CRUD logic
* **Integration Tests**: PostgreSQL for real behavior
    * Schema validation against actual database
    * PostgreSQL-specific features (enums, JSON)
    * Transaction behavior
    * Audit logging
    * Query performance

### 7.2 Test Database Setup

**Using Alembic Migrations**

```python
# conftest.py
import pytest
from sqlmodel import create_engine, Session
from alembic import command
from alembic.config import Config

@pytest.fixture(scope="session")
def postgres_test_db():
    """Create PostgreSQL test database from Alembic migration."""
    # Create test database
    engine = create_engine("postgresql://localhost/genew4_test")
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield engine
    
    # Teardown
    engine.dispose()
```

### 7.3 Test Fixtures

**Common Test Data**

```python
@pytest.fixture
def sample_gene():
    """Sample gene for testing."""
    return Gene(
        approved_symbol="BRCA1",
        approved_name="BRCA1 DNA repair associated",
        locus_type=GeneLocusType.GWPP,
        status=GeneStatus.APPROVED
    )

@pytest.fixture
def sample_gene_group():
    """Sample gene group for testing."""
    return GeneGroup(
        name="Tumor suppressor genes",
        status=GeneGroupStatus.EXPORTED
    )
```

### 7.4 Schema Validation Tests

**Verify ORM Matches Database**

```python
def test_gene_table_exists(postgres_session):
    """Verify hgnc table exists with correct columns."""
    inspector = inspect(postgres_session.get_bind())
    assert "hgnc" in inspector.get_table_names()
    
    columns = {col["name"] for col in inspector.get_columns("hgnc")}
    assert "hgnc_id" in columns
    assert "hgnc_app_sym" in columns
    # ... verify all expected columns

def test_gene_model_reflects_schema(postgres_session):
    """Verify Gene model fields match database schema."""
    # Create and retrieve a gene
    gene = Gene(approved_symbol="TEST", locus_type=GeneLocusType.GWPP, status=GeneStatus.PENDING)
    postgres_session.add(gene)
    postgres_session.commit()
    
    retrieved = postgres_session.get(Gene, gene.id)
    assert retrieved.approved_symbol == "TEST"
```

### 7.5 Test Execution

**Parallel Execution with pytest-xdist**

```bash
# Run unit tests (fast)
pytest tests/unit -n auto

# Run integration tests (slower)
pytest tests/integration

# Run all tests
pytest -n auto
```

### 7.6 Test Coverage Requirements

* Minimum 90% code coverage
* 100% coverage for models (field definitions, relationships)
* All CRUD operations tested
* All relationships traversable
* Audit logging verified
* Error cases covered (read-only violations, validation errors)

## 8. Schema Management

### 8.1 Model Definition

**Hand-Written SQLModel Classes**

* Follow TypeScript entity structure exactly
* One class per file in `models/` directory
* Match table names and column names from TypeScript
* Use `Field()` with `sa_column_kwargs` for PostgreSQL-specific features

**Example: Gene Model**

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum as SQLEnum, text
from datetime import date
from ..enums import GeneLocusType, GeneStatus

class Gene(SQLModel, table=True):
    __tablename__ = "hgnc"
    
    # Editing
    lock: str | None = Field(default=None, sa_column_kwargs={"name": "hgnc_lock"})
    
    # Core public fields
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "hgnc_id"}
    )
    approved_symbol: str = Field(max_length=255, sa_column_kwargs={"name": "hgnc_app_sym"})
    approved_name: str | None = Field(default=None, sa_column_kwargs={"name": "hgnc_app_name"})
    locus_type: GeneLocusType = Field(
        default=GeneLocusType.UNDEF,
        sa_column=Column(SQLEnum(GeneLocusType), name="hgnc_locus_type", nullable=False)
    )
    status: GeneStatus = Field(
        default=GeneStatus.PENDING,
        sa_column=Column(SQLEnum(GeneStatus), name="hgnc_status", nullable=False)
    )
    # ... additional fields
    
    # Relationships
    gene_has_gene_groups: list["GeneHasGeneGroup"] = Relationship(back_populates="gene")
```

### 8.2 Alembic Migrations

**Initial Migration from Existing Database**

```bash
# Generate initial migration from actual genew4 database
alembic revision --autogenerate -m "Initial schema from genew4"
```

**Purpose**

* Document existing schema
* Create test databases matching production
* Not for production schema changes (database already exists)

**Migration Files**

* Single initial migration: `001_initial_schema.py`
* Audit log table creation: `002_add_audit_log.py`

### 8.3 Schema Validation

**Automated Tests**

* Integration tests verify models match actual database
* Compare column names, types, constraints
* Verify relationships work as expected
* Run against real PostgreSQL instance

## 9. Documentation

### 9.1 Docstring Standards

**Google Style Docstrings**

```python
def get_gene_by_symbol(session: Session, symbol: str) -> Gene | None:
    """Retrieves a gene by its approved symbol.
    
    Args:
        session: Active database session.
        symbol: The approved gene symbol (e.g., "BRCA1").
        
    Returns:
        The gene if found, None otherwise.
        
    Example:
        >>> with get_readonly_session() as session:
        ...     gene = get_gene_by_symbol(session, "BRCA1")
        ...     print(gene.approved_name)
        BRCA1 DNA repair associated
    """
    stmt = select(Gene).where(Gene.approved_symbol == symbol)
    return session.exec(stmt).first()
```

**Coverage**

* All public functions and methods
* All model classes and fields
* Complex relationship patterns
* Non-obvious behavior

### 9.2 MkDocs Documentation

**Configuration (mkdocs.yml)**

```yaml
site_name: genew4-orm Documentation
site_description: Python ORM for the genew4 PostgreSQL database
theme:
  name: material
  palette:
    primary: indigo
  features:
    - navigation.sections
    - toc.integrate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            docstring_style: google

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Configuration: configuration.md
  - Models:
    - Overview: models.md
    - Core Models: models/core.md
    - Reference Models: models/reference.md
  - Usage:
    - Querying: querying.md
    - CRUD Operations: crud-operations.md
    - Audit Logging: audit-logging.md
  - Testing: testing.md
```

**Documentation Pages**

1. **index.md**: Project overview, features, quick links
2. **getting-started.md**: Installation, setup, first query
3. **configuration.md**: Environment variables, connection settings
4. **models.md**: Entity overview, relationships, field descriptions
5. **querying.md**: Read operations, eager loading, filtering, sorting
6. **crud-operations.md**: Read-only vs read-write sessions, creating, updating, deleting
7. **audit-logging.md**: How audit trail works, querying audit logs
8. **testing.md**: Running tests, writing new tests, fixtures

### 9.3 README.md

**Quick Start Focus**

````markdown
# genew4-orm

Python ORM for the genew4 PostgreSQL database.

## Installation

```bash
uv add genew4-orm
```

## Quick Example

```python
from genew4_orm import get_readonly_session
from genew4_orm.models import Gene
from sqlmodel import select

with get_readonly_session() as session:
    genes = session.exec(select(Gene).limit(10)).all()
    for gene in genes:
        print(f"{gene.approved_symbol}: {gene.approved_name}")
```

## Documentation

Full documentation: https://your-docs-site.com

## Features

* ✅ Type-safe models with Pydantic validation
* ✅ Read-only by default (safe mode)
* ✅ Full CRUD when needed
* ✅ Audit logging for all writes
* ✅ Comprehensive test suite
````

## 10. Package Distribution

### 10.1 Package Metadata

**pyproject.toml**

```toml
[project]
name = "genew4-orm"
version = "0.1.0"
description = "Python ORM for the genew4 PostgreSQL database"
authors = [{name = "Your Team"}]
readme = "README.md"
requires-python = ">=3.11"
license = {text = "Proprietary"}

dependencies = [
    "sqlmodel>=0.0.14",
    "psycopg[binary]>=3.1.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "alembic>=1.13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-xdist>=3.5.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
    "mkdocstrings[python]>=0.24.0",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=genew4_orm --cov-report=html --cov-report=term"
```

### 10.2 Versioning Strategy

**Semantic Versioning**

* **0.1.0**: Initial release with all 13 entities
* **0.2.0**: Performance optimizations, additional query helpers
* **0.x.y**: Bug fixes and minor enhancements
* **1.0.0**: Production-ready, stable API

**Version Bumping**

* Manual version updates in pyproject.toml
* Git tags for releases
* Changelog maintained in CHANGELOG.md

### 10.3 Installation Methods

**Via UV (recommended)**

```bash
uv add genew4-orm
```

**Via pip**

```bash
pip install genew4-orm
```

**Development Installation**

```bash
git clone https://github.com/your-org/genew4-orm.git
cd genew4-orm
uv sync --all-extras
```

## 11. Development Workflow

### 11.1 Code Quality Tools

**Ruff**: Linting and formatting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

**Mypy**: Type checking

```bash
mypy src/genew4_orm
```

**Pre-commit Integration**

* Run ruff and mypy before commits
* Ensure tests pass
* Verify coverage threshold

### 11.2 Testing Workflow

**During Development**

```bash
# Fast unit tests during coding
pytest tests/unit -n auto

# Integration tests before commit
pytest tests/integration

# Full suite before PR
pytest -n auto --cov=genew4_orm
```

### 11.3 Documentation Updates

**Build and Preview**

```bash
mkdocs serve  # Live preview at http://localhost:8000
```

**Deploy Documentation**

```bash
mkdocs build  # Generate static site in site/
```

## 12. Implementation Phases

### Phase 1: Foundation (Week 1)

* Project setup (UV, structure, pyproject.toml)
* Database configuration (Pydantic settings)
* Session management (read-only/read-write factories)
* Enum definitions (all 7 enums)
* Base model structure

### Phase 2: Core Models (Week 2)

* Gene model (complete with all 40+ fields)
* GeneGroup model
* GeneHasGeneGroup junction model
* Basic relationships
* Unit tests for models

### Phase 3: Remaining Models (Week 3)

* All 10 remaining entity models
* All relationships defined
* Hierarchy closure implementation
* Schema validation tests
* Integration tests

### Phase 4: Audit & Performance (Week 4)

* AuditLog model and table
* Audit logging implementation (event listeners)
* Query helper utilities
* Pre-optimized common queries
* Performance testing

### Phase 5: Documentation (Week 5)

* Google-style docstrings for all public APIs
* MkDocs site setup
* All documentation pages
* Code examples
* README polish

### Phase 6: Testing & Release (Week 6)

* Comprehensive test suite completion
* Coverage > 90%
* Integration test against real genew4 database
* Package build and installation testing
* Version 0.1.0 release

## 13. Success Metrics

### 13.1 Code Quality

* ✅ Mypy passes with strict mode
* ✅ Ruff linting passes with no errors
* ✅ Test coverage > 90%
* ✅ All models type-hinted
* ✅ All public APIs documented

### 13.2 Functionality

* ✅ All 13 entities implemented
* ✅ All relationships work bidirectionally
* ✅ Read-only sessions prevent writes
* ✅ Read-write sessions log to audit table
* ✅ Query helpers available for common patterns
* ✅ Schema matches existing genew4 database

### 13.3 Documentation

* ✅ MkDocs site builds successfully
* ✅ All pages complete with examples
* ✅ Getting started guide works end-to-end
* ✅ README clear and concise

### 13.4 Usability

* ✅ Package installable via uv/pip
* ✅ Configuration via environment variables works
* ✅ Team members can query database within 5 minutes of installation
* ✅ Clear error messages for common mistakes

## 14. Risks & Mitigations

### 14.1 Schema Drift

**Risk**: TypeScript and Python ORMs get out of sync

**Mitigation**:

* Schema validation tests catch mismatches
* Document process for updating both ORMs
* Consider generating from single source of truth in future

### 14.2 Performance Issues

**Risk**: N+1 queries or poor performance

**Mitigation**:

* Pre-optimized queries for common patterns
* Query helper documentation
* Performance benchmarks in integration tests
* Connection pooling enabled by default

### 14.3 Accidental Data Corruption

**Risk**: Team members accidentally modify production data

**Mitigation**:

* Read-only by default
* Explicit opt-in for writes
* Audit logging tracks all changes
* Clear documentation on safe practices

### 14.4 Complex Relationships

**Risk**: Hierarchy closure and self-referential relationships hard to implement

**Mitigation**:

* Reference TypeScript implementation closely
* Comprehensive tests for relationship traversal
* Documentation with examples
* Query helpers abstract complexity

## 15. Future Enhancements

### 15.1 Potential Additions

* Caching layer for reference data
* Async support (asyncpg)
* GraphQL interface
* REST API wrapper
* CLI tool for common operations
* Migration from TypeScript ORM
* Real-time change notifications

### 15.2 Not in Scope (Initial Release)

* Web UI or admin interface
* Authentication/authorization system (separate concern)
* Data migration tools
* Backup/restore functionality
* Multi-database support
* Replication/sharding

## 16. Appendix

### 16.1 Entity Mapping Reference

| TypeScript Entity   | Python Model        | Table Name             | Notes                         |
|---------------------|---------------------|------------------------|-------------------------------|
| Gene                | Gene                | hgnc                   | 40+ fields, 2 enums           |
| GeneGroup           | GeneGroup           | family_new             | Self-referential hierarchy    |
| GeneHasGeneGroup    | GeneHasGeneGroup    | gene_has_family        | Junction with custom sort     |
| GeneGroupAlias      | GeneGroupAlias      | family_alias           | One-to-many                   |
| HierarchyClosure    | HierarchyClosure    | hierarchy_closure      | Transitive closure            |
| Specialist          | Specialist          | specialist             | Many-to-many with GeneGroup   |
| ExternalResource    | ExternalResource    | external_resource      | Many-to-many with GeneGroup   |
| Correspondence      | Correspondence      | corr                   | Many-to-many with GeneGroup   |
| Editor              | Editor              | editor                 | Legacy users                  |
| User                | User                | user                   | Modern auth                   |
| Reminder            | Reminder            | reminder               | Links to Gene/GeneGroup       |
| Grch38Mapping       | Grch38Mapping       | coord_match_grch38     | Composite PK                  |
| Cytoband            | Cytoband            | cytoband               | Composite PK                  |

### 16.2 Key Dependencies

* **sqlmodel**: 0.0.14+ (ORM framework)
* **psycopg**: 3.1.0+ (PostgreSQL driver)
* **pydantic**: 2.5.0+ (Validation)
* **pydantic-settings**: 2.1.0+ (Configuration)
* **alembic**: 1.13.0+ (Migrations)
* **pytest**: 7.4.0+ (Testing)
* **pytest-xdist**: 3.5.0+ (Parallel testing)
* **ruff**: 0.1.0+ (Linting/formatting)
* **mypy**: 1.7.0+ (Type checking)
* **mkdocs**: 1.5.0+ (Documentation)
* **mkdocs-material**: 9.5.0+ (Documentation theme)

### 16.3 References

* TypeScript ORM: `/Users/kris/Repos/hgnc-tools-api`
* Existing Database: `genew4` PostgreSQL
* Team Size: 8 members
* Python Version: 3.11+
* Package Manager: UV
