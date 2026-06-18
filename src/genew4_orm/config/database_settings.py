"""Database connection settings backed by the shared ``db-common`` library.

``Genew4DatabaseSettings`` subclasses :class:`db_common.DatabaseSettings`,
inheriting its URL builder (``get_url``) and pool fields while overriding
only the genew4 specifics: the ``DATABASESETTINGS_`` env prefix, the
PostgreSQL defaults, the legacy ``DATABASESETTINGS_PG_*`` env-var names,
and the genew4-only ``pool_timeout`` field (db-common's engine layer does
not pass it; ``Genew4EngineFactory`` in ``session.py`` does, reading this
field).

Backward-compatibility shims keep legacy callers working without churn:

* ``pg_host`` / ``pg_port`` / ``pg_name`` / ``pg_user`` / ``pg_password`` —
  read/write properties over the canonical ``host`` / ``port`` / ``database``
  / ``username`` / ``password`` fields. They are *also* accepted as
  construction kwargs (mapped onto the canonical fields by a ``before``
  model validator) and read from the legacy ``DATABASESETTINGS_PG_*`` env
  vars, in addition to the canonical ``DATABASESETTINGS_HOST`` etc.
* ``get_connection_url(with_password=)`` — a string rendered from
  :meth:`get_url` (db-common), with the password omitted unless requested.
* ``get_engine_kwargs()`` — pool kwargs (including ``pool_timeout``) read
  from the inherited fields.
* ``DatabaseSettings`` — a module alias of this class (see below).

Notes on intentional behaviour changes versus the pre-migration settings:

* The password is a plain ``str`` (was ``pydantic.SecretStr``) to align
  with db-common's ``password: str | None``. ``.get_secret_value()`` is gone.
* ``get_async_engine_kwargs()`` is removed — db-common's engine/session
  layer is synchronous only.
* Port / pool-numeric ``ge``/``le`` validators are dropped to match
  db-common's unconstrained pool fields.
"""

from typing import Any

import db_common
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class Genew4DatabaseSettings(db_common.DatabaseSettings):
    """Connection and pooling settings for the genew4 PostgreSQL database.

    Subclass the shared :class:`db_common.DatabaseSettings`, overriding only
    the genew4 specifics and re-exposing the legacy ``pg_*`` surface as
    aliases of the inherited canonical fields.
    """

    model_config = SettingsConfigDict(
        env_prefix="DATABASESETTINGS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # -- Driver / connection defaults ---------------------------------------
    driver: str = "postgresql+psycopg"
    host: str | None = Field(
        default="localhost",
        validation_alias=AliasChoices("DATABASESETTINGS_HOST", "DATABASESETTINGS_PG_HOST"),
        description="PostgreSQL server hostname.",
    )
    port: int | None = Field(
        default=5432,
        validation_alias=AliasChoices("DATABASESETTINGS_PORT", "DATABASESETTINGS_PG_PORT"),
        description="PostgreSQL server port.",
    )
    database: str | None = Field(
        default="genew4",
        validation_alias=AliasChoices("DATABASESETTINGS_DATABASE", "DATABASESETTINGS_PG_NAME"),
        description="Database name.",
    )
    username: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASESETTINGS_USERNAME", "DATABASESETTINGS_PG_USER"),
        description="Database username.",
    )
    password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASESETTINGS_PASSWORD", "DATABASESETTINGS_PG_PASSWORD"),
        description="Database password (plain str, per db-common).",
        repr=False,
    )

    # -- genew4-only pool field ---------------------------------------------
    # db-common's EngineFactory does not pass pool_timeout; Genew4EngineFactory
    # (session.py) reads this field when creating the engine.
    pool_timeout: int = Field(default=30, description="Connection pool timeout in seconds.")

    # -- Legacy ``pg_*`` construction kwarg mapping --------------------------
    @model_validator(mode="before")
    @classmethod
    def _map_legacy_pg_kwargs(cls, data: Any) -> Any:
        """Map legacy ``pg_*`` construction kwargs onto the canonical fields.

        ``pg_*`` are exposed as properties below (not fields), so without this
        remapper pydantic would reject ``Genew4DatabaseSettings(pg_host=...)``.
        """
        if isinstance(data, dict):
            legacy_to_canonical = {
                "pg_host": "host",
                "pg_port": "port",
                "pg_name": "database",
                "pg_user": "username",
                "pg_password": "password",
            }
            for legacy, canonical in legacy_to_canonical.items():
                if legacy in data:
                    data.setdefault(canonical, data.pop(legacy))
        return data

    # -- Legacy ``pg_*`` read/write property aliases ------------------------
    @property
    def pg_host(self) -> str | None:
        """Alias for :attr:`host`."""
        return self.host

    @pg_host.setter
    def pg_host(self, value: str | None) -> None:
        self.host = value

    @property
    def pg_port(self) -> int | None:
        """Alias for :attr:`port`."""
        return self.port

    @pg_port.setter
    def pg_port(self, value: int | None) -> None:
        self.port = value

    @property
    def pg_name(self) -> str | None:
        """Alias for :attr:`database`."""
        return self.database

    @pg_name.setter
    def pg_name(self, value: str | None) -> None:
        self.database = value

    @property
    def pg_user(self) -> str | None:
        """Alias for :attr:`username`."""
        return self.username

    @pg_user.setter
    def pg_user(self, value: str | None) -> None:
        self.username = value

    @property
    def pg_password(self) -> str | None:
        """Alias for :attr:`password`."""
        return self.password

    @pg_password.setter
    def pg_password(self, value: str | None) -> None:
        self.password = value

    # -- Compat shims delegating to db-common -------------------------------
    def get_connection_url(self, *, with_password: bool = False) -> str:
        """Build the PostgreSQL connection URL as a string.

        Delegates to db-common's :meth:`get_url`. By default the password is
        omitted entirely (legacy behaviour); pass ``with_password=True`` for
        a URL suitable for :func:`sqlalchemy.create_engine`.

        Args:
            with_password: If True, include the password in the URL.

        Returns:
            The psycopg connection URL string.
        """
        url: URL = self.get_url()
        if not with_password:
            # SQLAlchemy's ``URL.set(password=None)`` is a no-op (None means
            # "unchanged" in 2.0), so rebuild without the password to omit it.
            url = URL.create(
                drivername=url.drivername,
                username=url.username,
                host=url.host,
                port=url.port,
                database=url.database,
            )
        return url.render_as_string(hide_password=False)

    def get_engine_kwargs(self) -> dict[str, Any]:
        """Get SQLAlchemy engine creation arguments.

        Reads the inherited pool fields plus the genew4-only ``pool_timeout``.

        Returns:
            Dictionary of keyword arguments for ``create_engine()``.
        """
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": self.pool_pre_ping,
        }


# Backward-compat alias: the class was historically named ``DatabaseSettings``
# and is imported under that name throughout the codebase (session.py,
# alembic/env.py, conftest.py, config/__init__.py, and the test suite). Keeping
# the alias avoids touching those callers.
DatabaseSettings = Genew4DatabaseSettings
