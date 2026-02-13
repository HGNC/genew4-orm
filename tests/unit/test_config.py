"""Unit tests for config module."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from genew4_orm.config import DatabaseSettings


class TestDatabaseSettings:
    """Test cases for DatabaseSettings class."""

    def test_database_settings_defaults(self) -> None:
        """Test DatabaseSettings with default values."""
        # Set required environment variables
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings()

            assert settings.pg_host == "localhost"
            assert settings.pg_port == 5432
            assert settings.pg_name == "genew4"
            assert settings.pg_user == "testuser"
            assert settings.pg_password.get_secret_value() == "testpass"

    def test_database_settings_from_env(self) -> None:
        """Test DatabaseSettings loading from environment variables."""
        env_vars = {
            "DATABASESETTINGS_PG_HOST": "testhost",
            "DATABASESETTINGS_PG_PORT": "5433",
            "DATABASESETTINGS_PG_NAME": "testdb",
            "DATABASESETTINGS_PG_USER": "testuser",
            "DATABASESETTINGS_PG_PASSWORD": "testpass",
            "DATABASESETTINGS_POOL_SIZE": "10",
            "DATABASESETTINGS_MAX_OVERFLOW": "20",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.pg_host == "testhost"
            assert settings.pg_port == 5433
            assert settings.pg_name == "testdb"
            assert settings.pg_user == "testuser"
            assert settings.pg_password.get_secret_value() == "testpass"
            assert settings.pool_size == 10
            assert settings.max_overflow == 20

    def test_database_settings_port_validation_minimum(self) -> None:
        """Test that port validation rejects values below 1."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass", "DATABASESETTINGS_PG_PORT": "0"}):
            with pytest.raises(ValidationError) as exc_info:
                DatabaseSettings()

            # Pydantic v2 error message format
            error_str = str(exc_info.value)
            assert "greater_than_equal" in error_str.lower() or "port" in error_str.lower()

    def test_database_settings_port_validation_maximum(self) -> None:
        """Test that port validation rejects values above 65535."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass", "DATABASESETTINGS_PG_PORT": "65536"}):
            with pytest.raises(ValidationError) as exc_info:
                DatabaseSettings()

            # Pydantic v2 error message format
            assert "less_than_equal" in str(exc_info.value).lower() or "port" in str(exc_info.value).lower()

    def test_database_settings_port_validation_negative(self) -> None:
        """Test that port validation rejects negative values."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass", "DATABASESETTINGS_PG_PORT": "-1"}):
            with pytest.raises(ValidationError) as exc_info:
                DatabaseSettings()

            # Pydantic v2 error message format
            assert "greater_than_equal" in str(exc_info.value).lower() or "port" in str(exc_info.value).lower()

    def test_database_settings_port_boundary_valid(self) -> None:
        """Test that port boundary values 1 and 65535 are valid."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            # Test minimum valid port
            settings_min = DatabaseSettings(pg_port=1)
            assert settings_min.pg_port == 1

            # Test maximum valid port
            settings_max = DatabaseSettings(pg_port=65535)
            assert settings_max.pg_port == 65535

    def test_database_settings_pool_size_validation(self) -> None:
        """Test that pool_size validates range constraints."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            # Valid pool size
            settings = DatabaseSettings(pool_size=50)
            assert settings.pool_size == 50

    def test_database_settings_max_overflow_validation(self) -> None:
        """Test that max_overflow validates range constraints."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings(max_overflow=50)
            assert settings.max_overflow == 50

    def test_database_settings_pool_timeout_validation(self) -> None:
        """Test that pool_timeout validates range constraints."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings(pool_timeout=60)
            assert settings.pool_timeout == 60

    def test_database_settings_pool_recycle_validation(self) -> None:
        """Test that pool_recycle validates range constraints."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings(pool_recycle=1800)
            assert settings.pool_recycle == 1800


class TestGetConnectionUrl:
    """Test cases for get_connection_url method."""

    def test_get_connection_url_without_password(self) -> None:
        """Test get_connection_url without password (default)."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings()

            url = settings.get_connection_url()

            assert "postgresql+psycopg://" in url
            assert "testuser" in url
            assert "localhost" in url
            assert "5432" in url
            assert "genew4" in url
            # Password should not be included
            assert ":testpass@" not in url

    def test_get_connection_url_with_password(self) -> None:
        """Test get_connection_url with password."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass123"}):
            settings = DatabaseSettings(pg_host="db.example.com", pg_port=5433, pg_name="testdb")

            url = settings.get_connection_url(with_password=True)

            assert url == "postgresql+psycopg://testuser:testpass123@db.example.com:5433/testdb"

    def test_get_connection_url_custom_settings(self) -> None:
        """Test get_connection_url with custom settings."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "customuser", "DATABASESETTINGS_PG_PASSWORD": "custompass"}):
            settings = DatabaseSettings(
                pg_host="custom.host.com",
                pg_port=3306,
                pg_name="customdb",
            )

            url = settings.get_connection_url(with_password=True)

            assert url == "postgresql+psycopg://customuser:custompass@custom.host.com:3306/customdb"


class TestGetEngineKwargs:
    """Test cases for get_engine_kwargs method."""

    def test_get_engine_kwargs_default(self) -> None:
        """Test get_engine_kwargs returns expected defaults."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings()

            kwargs = settings.get_engine_kwargs()

            assert kwargs["pool_size"] == 5
            assert kwargs["max_overflow"] == 10
            assert kwargs["pool_timeout"] == 30
            assert kwargs["pool_recycle"] == 3600
            assert kwargs["pool_pre_ping"] is True

    def test_get_engine_kwargs_custom_pool_settings(self) -> None:
        """Test get_engine_kwargs with custom pool settings."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
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


class TestGetAsyncEngineKwargs:
    """Test cases for get_async_engine_kwargs method."""

    def test_get_async_engine_kwargs_default(self) -> None:
        """Test get_async_engine_kwargs returns expected defaults."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings()

            kwargs = settings.get_async_engine_kwargs()

            assert kwargs["pool_size"] == 5
            assert kwargs["max_overflow"] == 10
            assert kwargs["pool_timeout"] == 30
            assert kwargs["pool_recycle"] == 3600
            assert kwargs["pool_pre_ping"] is True

    def test_get_async_engine_kwargs_custom_settings(self) -> None:
        """Test get_async_engine_kwargs with custom settings."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "testpass"}):
            settings = DatabaseSettings(
                pool_size=20,
                max_overflow=30,
                pool_timeout=90,
                pool_recycle=5400,
            )

            kwargs = settings.get_async_engine_kwargs()

            assert kwargs["pool_size"] == 20
            assert kwargs["max_overflow"] == 30
            assert kwargs["pool_timeout"] == 90
            assert kwargs["pool_recycle"] == 5400
            assert kwargs["pool_pre_ping"] is True


class TestSecretStr:
    """Test cases for password as SecretStr."""

    def test_password_is_secret_str(self) -> None:
        """Test that password field is a SecretStr."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "secret123"}):
            settings = DatabaseSettings()

            # Should be able to get secret value
            assert settings.pg_password.get_secret_value() == "secret123"

    def test_password_repr_does_not_leak(self) -> None:
        """Test that repr of settings doesn't leak password."""
        with patch.dict(os.environ, {"DATABASESETTINGS_PG_USER": "testuser", "DATABASESETTINGS_PG_PASSWORD": "secret123"}):
            settings = DatabaseSettings()

            repr_str = repr(settings)
            assert "secret123" not in repr_str
