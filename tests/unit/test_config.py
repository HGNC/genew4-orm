"""Unit tests for the ``Genew4DatabaseSettings`` config module.

These pin the contract introduced in T3 of the db-common migration:
``Genew4DatabaseSettings`` subclasses ``db_common.DatabaseSettings``,
keeps the ``DATABASESETTINGS_`` env prefix and PostgreSQL defaults,
maps the legacy ``DATABASESETTINGS_PG_*`` env vars onto the inherited
canonical fields via ``AliasChoices``, exposes ``pg_*`` read/write
property aliases, preserves ``get_connection_url``/``get_engine_kwargs``
as compat shims delegating to ``db_common``'s ``get_url()``, adds a
``pool_timeout`` field (default 30), drops ``SecretStr``, and removes
``get_async_engine_kwargs`` entirely.

``DatabaseSettings`` (the unchanged public alias) is exercised
throughout; after T3 it is literally ``Genew4DatabaseSettings``.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from sqlalchemy import URL

from genew4_orm.config import DatabaseSettings


class TestGenew4DatabaseSettingsDefaults:
    """Defaults and config inherited/overridden from db_common.DatabaseSettings."""

    def test_database_settings_alias_is_genew4_subclass(self) -> None:
        """The public alias points at a db_common.DatabaseSettings subclass."""
        import db_common

        from genew4_orm.config.database_settings import Genew4DatabaseSettings

        assert DatabaseSettings is Genew4DatabaseSettings
        assert issubclass(Genew4DatabaseSettings, db_common.DatabaseSettings)

    def test_env_prefix_preserved(self) -> None:
        """The DATABASESETTINGS_ env prefix is preserved."""
        assert DatabaseSettings.model_config["env_prefix"] == "DATABASESETTINGS_"

    def test_postgresql_defaults(self) -> None:
        """PG defaults match the historical genew4 configuration."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.driver == "postgresql+psycopg"
            assert settings.host == "localhost"
            assert settings.port == 5432
            assert settings.database == "genew4"
            assert settings.pool_size == 5
            assert settings.max_overflow == 10
            assert settings.pool_recycle == 3600
            assert settings.pool_timeout == 30
            assert settings.pool_pre_ping is True


class TestEnvOverrides:
    """Both the legacy PG_* and canonical env var spellings must work."""

    def test_legacy_pg_env_overrides(self) -> None:
        """DATABASESETTINGS_PG_HOST/PORT/NAME/USER/PASSWORD still drive settings."""
        env_vars = {
            "DATABASESETTINGS_PG_HOST": "testhost",
            "DATABASESETTINGS_PG_PORT": "5433",
            "DATABASESETTINGS_PG_NAME": "testdb",
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
            "DATABASESETTINGS_POOL_TIMEOUT": "60",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.host == "testhost"
            assert settings.port == 5433
            assert settings.database == "testdb"
            assert settings.username == "testuser"
            assert settings.password == "testpass"
            assert settings.pool_timeout == 60

    def test_canonical_env_overrides(self) -> None:
        """The inherited canonical DATABASESETTINGS_HOST/USERNAME/... names work too."""
        env_vars = {
            "DATABASESETTINGS_HOST": "canonhost",
            "DATABASESETTINGS_PORT": "5500",
            "DATABASESETTINGS_DATABASE": "canondb",
            "DATABASESETTINGS_USERNAME": "canonuser",
            "DATABASESETTINGS_PASSWORD": "canonpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.host == "canonhost"
            assert settings.port == 5500
            assert settings.database == "canondb"
            assert settings.username == "canonuser"
            assert settings.password == "canonpass"

    def test_inherited_pool_fields_load_from_env(self) -> None:
        """The inherited pool fields (pool_size/max_overflow/pool_recycle) still
        load from their DATABASESETTINGS_* env vars, restoring the coverage the
        pre-migration suite had."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
            "DATABASESETTINGS_POOL_SIZE": "42",
            "DATABASESETTINGS_MAX_OVERFLOW": "77",
            "DATABASESETTINGS_POOL_RECYCLE": "1800",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.pool_size == 42
            assert settings.max_overflow == 77
            assert settings.pool_recycle == 1800


class TestRequiredFields:
    """username/password stay required for the (non-sqlite) PG driver."""

    def test_username_password_required(self) -> None:
        """Constructing without credentials raises ValidationError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError):
                DatabaseSettings()

    def test_password_missing_raises(self) -> None:
        """Missing only the password still raises."""
        env_vars = {"DATABASESETTINGS_PG_USER": "testuser"}
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                DatabaseSettings()


class TestPgAliases:
    """pg_* properties alias the inherited canonical fields (read + write + kwarg)."""

    def test_pg_properties_alias_canonical_fields(self) -> None:
        """Reading pg_* returns the canonical field values."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.pg_host == settings.host == "localhost"
            assert settings.pg_port == settings.port == 5432
            assert settings.pg_name == settings.database == "genew4"
            assert settings.pg_user == settings.username == "testuser"
            assert settings.pg_password == settings.password == "testpass"

    def test_pg_property_setters_update_canonical_fields(self) -> None:
        """Writing pg_* propagates to the canonical fields."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            settings.pg_host = "newhost"
            settings.pg_user = "newuser"
            settings.pg_password = "newpass"

            assert settings.host == "newhost"
            assert settings.username == "newuser"
            assert settings.password == "newpass"

    def test_legacy_pg_constructor_kwargs_accepted(self) -> None:
        """Legacy pg_* construction kwargs map onto the canonical fields."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings(
                pg_host="kw.example.com",
                pg_port=4242,
                pg_name="kwdb",
            )

            assert settings.host == "kw.example.com"
            assert settings.port == 4242
            assert settings.database == "kwdb"
            assert settings.pg_host == "kw.example.com"


class TestGetUrl:
    """get_url() is inherited from db_common and returns a sqlalchemy.URL."""

    def test_get_url_returns_sqlalchemy_url(self) -> None:
        """get_url() returns a sqlalchemy.engine.URL."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            url = settings.get_url()

            assert isinstance(url, URL)
            assert url.drivername == "postgresql+psycopg"
            assert url.host == "localhost"
            assert url.port == 5432
            assert url.database == "genew4"
            assert url.username == "testuser"


class TestGetConnectionUrl:
    """get_connection_url() compat shim delegates to db_common's get_url()."""

    def test_get_connection_url_with_password_default_settings(self) -> None:
        """with_password=True renders the full psycopg URL for default settings."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            url = settings.get_connection_url(with_password=True)

            assert url == "postgresql+psycopg://testuser:testpass@localhost:5432/genew4"

    def test_get_connection_url_without_password_omits_password(self) -> None:
        """with_password=False omits the password entirely (legacy behaviour)."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            url = settings.get_connection_url()  # default with_password=False

            assert url == "postgresql+psycopg://testuser@localhost:5432/genew4"
            assert "testpass" not in url
            assert ":testpass@" not in url

    def test_get_connection_url_with_custom_settings(self) -> None:
        """Custom host/port/database/user/password render into the URL."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "customuser",
            "DATABASESETTINGS_PG_PASSWORD": "custompass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings(
                host="custom.host.com",
                port=3306,
                database="customdb",
            )

            url = settings.get_connection_url(with_password=True)

            assert url == "postgresql+psycopg://customuser:custompass@custom.host.com:3306/customdb"


class TestGetEngineKwargs:
    """get_engine_kwargs() compat shim reads the inherited pool fields + pool_timeout."""

    def test_get_engine_kwargs_default(self) -> None:
        """Default pool kwargs include pool_timeout and the inherited fields."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            kwargs = settings.get_engine_kwargs()

            assert kwargs == {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "pool_pre_ping": True,
            }

    def test_get_engine_kwargs_custom_pool_settings(self) -> None:
        """Custom pool settings flow through get_engine_kwargs."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings(
                pool_size=15,
                max_overflow=25,
                pool_timeout=60,
                pool_recycle=7200,
            )

            kwargs = settings.get_engine_kwargs()

            assert kwargs["pool_size"] == 15
            assert kwargs["max_overflow"] == 25
            assert kwargs["pool_timeout"] == 60
            assert kwargs["pool_recycle"] == 7200
            assert kwargs["pool_pre_ping"] is True


class TestAsyncHelperRemoved:
    """get_async_engine_kwargs() is dropped (db-common is sync-only)."""

    def test_get_async_engine_kwargs_does_not_exist_on_instance(self) -> None:
        """The instance no longer exposes get_async_engine_kwargs."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert not hasattr(settings, "get_async_engine_kwargs")

    def test_get_async_engine_kwargs_not_defined_on_class(self) -> None:
        """The class no longer defines get_async_engine_kwargs."""
        with pytest.raises(AttributeError):
            _ = DatabaseSettings.get_async_engine_kwargs  # noqa: B018


class TestPasswordIsPlainStr:
    """The password is a plain str now (SecretStr dropped to align with db-common)."""

    def test_password_is_str_not_secretstr(self) -> None:
        """password is a plain str with no get_secret_value()."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "secret123",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.password == "secret123"
            assert isinstance(settings.password, str)
            assert not hasattr(settings.password, "get_secret_value")

    def test_pg_password_property_returns_plain_str(self) -> None:
        """pg_password property returns the same plain str as password."""
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "secret123",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.pg_password == "secret123"
            assert isinstance(settings.pg_password, str)

    def test_password_not_leaked_in_repr_or_str(self) -> None:
        """repr()/str() of settings must not render the plaintext password.

        Regression guard: the pre-migration SecretStr masked the password in
        repr; dropping it for a plain str (to align with db-common) reintroduced
        plaintext leakage via pydantic's generated __repr__. Field(repr=False)
        restores the masking while keeping password a str.
        """
        secret = "supersecret123"
        env_vars = {
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": secret,
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert secret not in repr(settings)
            assert secret not in str(settings)
