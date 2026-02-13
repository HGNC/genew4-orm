"""Alembic environment configuration for genew4-orm.

This module configures Alembic migration environment for genew4-orm project.
It supports both online and offline migration modes.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import DatabaseSettings for URL resolution
# Import all models to ensure they're registered with SQLAlchemy
# This must be done before we can use autogenerate
import genew4_orm.models  # noqa: F401
from genew4_orm.config import DatabaseSettings

# this is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# For SQLModel, we need to get metadata from SQLModel declarative base
# The target_metadata will be used by autogenerate to detect model changes
target_metadata = SQLModel.metadata

# Set the database URL from environment variables
# This allows alembic to use same configuration as application
try:
    settings = DatabaseSettings()
    db_url = settings.get_connection_url(with_password=True)
    config.set_main_option("sqlalchemy.url", db_url)
except Exception:
    # If DatabaseSettings fails, use default from alembic.ini
    pass


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Override sqlalchemy.url with actual connection URL
    # This ensures environment variables are respected
    try:
        settings = DatabaseSettings()
        configuration = config.get_section(config.config_ini_section, {})
        configuration["sqlalchemy.url"] = settings.get_connection_url(with_password=True)

        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    except Exception:
        # Fall back to default configuration
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
