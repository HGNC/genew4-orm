"""Database configuration settings using Pydantic settings."""

from typing import Any
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection and pool configuration.

    Attributes:
        pg_host: PostgreSQL server hostname or IP address.
        pg_port: PostgreSQL server port (default: 5432).
        pg_name: Database name (default: 'genew4').
        pg_user: Database username.
        pg_password: Database password (stored securely as SecretStr).
        pool_size: Number of persistent connections to maintain (default: 5).
        max_overflow: Maximum overflow connections beyond pool_size (default: 10).
        pool_timeout: Connection timeout in seconds (default: 30).
        pool_recycle: Recycle connections after this many seconds (default: 3600).
    """

    model_config = SettingsConfigDict(
        env_prefix="DATABASESETTINGS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pg_host: str = Field(default="localhost", description="PostgreSQL server hostname")
    pg_port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL server port")
    pg_name: str = Field(default="genew4", description="Database name")
    pg_user: str = Field(description="Database username")
    pg_password: SecretStr = Field(description="Database password")

    # Connection pool settings
    pool_size: int = Field(default=5, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(
        default=10, ge=0, le=100, description="Maximum overflow connections"
    )
    pool_timeout: int = Field(
        default=30, ge=1, le=300, description="Connection timeout in seconds"
    )
    pool_recycle: int = Field(
        default=3600, ge=0, description="Recycle connections after this many seconds"
    )

    def get_connection_url(self, *, with_password: bool = False) -> str:
        """Build PostgreSQL connection URL.

        Args:
            with_password: If True, include password in the URL.
                Use with caution - only for trusted environments.

        Returns:
            The PostgreSQL connection URL using psycopg driver.
        """
        password_part = ""
        if with_password:
            password_part = f":{self.pg_password.get_secret_value()}"

        return (
            f"postgresql+psycopg://{self.pg_user}{password_part}@"
            f"{self.pg_host}:{self.pg_port}/{self.pg_name}"
        )

    def get_engine_kwargs(self) -> dict[str, Any]:
        """Get SQLAlchemy engine creation arguments.

        Returns:
            Dictionary of keyword arguments for create_engine().
        """
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": True,  # Verify connections before using
        }

    def get_async_engine_kwargs(self) -> dict[str, Any]:
        """Get SQLAlchemy async engine creation arguments.

        Returns:
            Dictionary of keyword arguments for create_async_engine().
        """
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": True,
        }
