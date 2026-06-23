# Configuration

genew4-orm uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management, layered on top of the shared [db-common](https://github.com/HGNC/db-common) `DatabaseSettings`. All settings can be loaded from environment variables or passed directly.

## Environment Variables

Create a `.env` file in your project root. All variables are prefixed with
`DATABASESETTINGS_`; the `DATABASESETTINGS_PG_*` names are accepted as legacy
aliases:

```bash
# PostgreSQL Configuration
DATABASESETTINGS_PG_HOST=localhost
DATABASESETTINGS_PG_PORT=5432
DATABASESETTINGS_PG_NAME=genew4
DATABASESETTINGS_PG_USER=your_username
DATABASESETTINGS_PG_PASSWORD=your_password

# Connection Pool Settings (Optional)
DATABASESETTINGS_POOL_SIZE=5
DATABASESETTINGS_MAX_OVERFLOW=10
DATABASESETTINGS_POOL_TIMEOUT=30
DATABASESETTINGS_POOL_RECYCLE=3600
DATABASESETTINGS_POOL_PRE_PING=true
```

## Genew4DatabaseSettings Class

The canonical class is `Genew4DatabaseSettings` (a subclass of
`db_common.DatabaseSettings`). It is re-exported as `DatabaseSettings` for
backwards compatibility:

```python
from genew4_orm.config import DatabaseSettings

# Load from environment variables
settings = DatabaseSettings()

# Or pass values directly (canonical field names)
settings = DatabaseSettings(
    host="localhost",
    port=5432,
    database="genew4",
    username="username",
    password="password",
)
```

The legacy `pg_host` / `pg_port` / `pg_name` / `pg_user` / `pg_password`
keyword arguments still work as aliases of the canonical fields.

## Configuration Options

### Driver and PostgreSQL Connection

| Field | Env var (legacy alias) | Type | Default | Description |
|-------|------------------------|------|---------|-------------|
| `driver` | `DATABASESETTINGS_DRIVER` | `str` | `"postgresql+psycopg"` | SQLAlchemy driver string |
| `host` | `DATABASESETTINGS_HOST` (`..._PG_HOST`) | `str \| None` | `"localhost"` | PostgreSQL server hostname |
| `port` | `DATABASESETTINGS_PORT` (`..._PG_PORT`) | `int \| None` | `5432` | PostgreSQL server port |
| `database` | `DATABASESETTINGS_DATABASE` (`..._PG_NAME`) | `str \| None` | `"genew4"` | Database name |
| `username` | `DATABASESETTINGS_USERNAME` (`..._PG_USER`) | `str \| None` | *(required)* | Database username |
| `password` | `DATABASESETTINGS_PASSWORD` (`..._PG_PASSWORD`) | `str \| None` | *(required)* | Database password (plain `str`) |

> Note: `password` is a plain `str` (it was `pydantic.SecretStr` before the
> db-common migration, so `.get_secret_value()` is no longer available).

### Connection Pool

| Field | Env var | Type | Default | Description |
|-------|---------|------|---------|-------------|
| `pool_size` | `DATABASESETTINGS_POOL_SIZE` | `int` | `5` | Number of persistent connections |
| `max_overflow` | `DATABASESETTINGS_MAX_OVERFLOW` | `int` | `10` | Maximum overflow connections |
| `pool_timeout` | `DATABASESETTINGS_POOL_TIMEOUT` | `int` | `30` | Connection timeout (seconds) — genew4 only |
| `pool_recycle` | `DATABASESETTINGS_POOL_RECYCLE` | `int` | `3600` | Recycle connections after N seconds |
| `pool_pre_ping` | `DATABASESETTINGS_POOL_PRE_PING` | `bool` | `true` | Test connections before checkout |

`pool_timeout` is a genew4-specific field; db-common's own engine layer does not
pass it, but `Genew4EngineFactory` reads it when creating the engine.

### Character Set / Collation

| Field | Env var | Type | Default | Description |
|-------|---------|------|---------|-------------|
| `charset` | `DATABASESETTINGS_CHARSET` | `str` | `"utf8mb4"` | Connection charset (inherited from db-common v0.2.0+) |
| `collation` | `DATABASESETTINGS_COLLATION` | `str \| None` | _(empty)_ | Optional connection collation (inherited from db-common v0.2.0+) |

> The `charset`/`collation` fields are inherited from db-common (v0.2.0+), where
> db-common enforces `charset` on every pooled MySQL connection at connect time
> via `SET NAMES` (and `COLLATE <collation>` when `collation` is set). genew4-orm
> uses the `postgresql+psycopg` driver, so these fields are **accepted but a
> no-op** here — the connect-time charset listener only registers for MySQL
> drivers.

## Connection URL

`Genew4DatabaseSettings` inherits a `get_url()` method (from db-common) that
returns a SQLAlchemy [`URL`](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.engine.URL),
and a genew4 convenience method `get_connection_url()` that renders a string:

```python
from genew4_orm.config import DatabaseSettings

settings = DatabaseSettings()

# SQLAlchemy URL object (used internally by create_engine)
url = settings.get_url()

# String form, password omitted by default
str_url = settings.get_connection_url()
# Returns: postgresql+psycopg://username@localhost:5432/genew4

# String form including the password
str_url = settings.get_connection_url(with_password=True)
# Returns: postgresql+psycopg://username:password@localhost:5432/genew4
```

`get_engine_kwargs()` returns the pool keyword arguments (including
`pool_timeout`) suitable for `sqlalchemy.create_engine()`:

```python
settings.get_engine_kwargs()
# {'pool_size': 5, 'max_overflow': 10, 'pool_timeout': 30,
#  'pool_recycle': 3600, 'pool_pre_ping': True}
```

## Engine Initialization

Initialize the global database engine:

```python
from genew4_orm.session import initialize_engine

# Load settings from environment
engine = initialize_engine()

# Or pass custom settings
from genew4_orm.config import DatabaseSettings
settings = DatabaseSettings(...)
engine = initialize_engine(settings)
```

`initialize_engine()` is idempotent: calling it a second time returns the
already-cached engine. Use `refresh_engine()` to rebuild the engine after
configuration changes, and `get_settings()` / `get_engine()` to read back the
cached singletons.

## Session Management

After initialization, create sessions for database operations:

### Read-Write Session

For operations that modify data. Pass `user=` so writes can be attributed in
the audit log:

```python
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="username") as session:
    # Write operations allowed
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated"
    # The session commits automatically on a clean exit (rolls back on error).
```

### Read-Only Session

For queries only. Any commit attempt raises
`db_common.ReadOnlySessionError`:

```python
from sqlalchemy import select

from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    # Read operations only
    results = session.scalars(select(Gene)).all()
```

## Closing Connections

When shutting down your application:

```python
from genew4_orm.session import close_all_sessions

close_all_sessions()
```
