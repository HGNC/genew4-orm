# Configuration

genew4-orm uses Pydantic Settings for configuration management. All settings can be loaded from environment variables or passed directly.

## Environment Variables

Create a `.env` file in your project root:

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
```

## DatabaseSettings Class

```python
from genew4_orm.config import DatabaseSettings

# Load from environment variables
settings = DatabaseSettings()

# Or pass values directly
settings = DatabaseSettings(
    pg_host="localhost",
    pg_port=5432,
    pg_name="genew4",
    pg_user="username",
    pg_password="password",
)
```

## Configuration Options

### PostgreSQL Connection

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pg_host` | `str` | `"localhost"` | PostgreSQL server hostname |
| `pg_port` | `int` | `5432` | PostgreSQL server port (1-65535) |
| `pg_name` | `str` | `"genew4"` | Database name |
| `pg_user` | `str` | *(required)* | Database username |
| `pg_password` | `SecretStr` | *(required)* | Database password |

### Connection Pool

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pool_size` | `int` | `5` | Number of persistent connections |
| `max_overflow` | `int` | `10` | Maximum overflow connections |
| `pool_timeout` | `int` | `30` | Connection timeout (seconds) |
| `pool_recycle` | `int` | `3600` | Recycle connections after N seconds |

## Connection URL

The `DatabaseSettings.get_connection_url()` method builds the PostgreSQL connection URL:

```python
from genew4_orm.config import DatabaseSettings

settings = DatabaseSettings()
url = settings.get_connection_url(with_password=True)
# Returns: postgresql+psycopg://user:password@localhost:5432/genew4

url_without_password = settings.get_connection_url(with_password=False)
# Returns: postgresql+psycopg://user@localhost:5432/genew4
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

## Session Management

After initialization, create sessions for database operations:

### Read-Write Session

For operations that modify data:

```python
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="username") as session:
    # Write operations allowed
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated"
    session.commit()
```

### Read-Only Session

For queries only (prevents accidental modifications):

```python
from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    # Read operations only
    from sqlmodel import select
    results = session.exec(select(Gene)).all()
```

## Closing Connections

When shutting down your application:

```python
from genew4_orm.session import close_all_sessions

close_all_sessions()
```
