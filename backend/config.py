"""
Application Configuration
=========================

This module handles the application's configuration by loading environment
variables from `.env` files and defining configuration classes for different
environments (e.g., Development, Production).

It uses a class-based approach where a base `Config` class holds all common
configuration variables, and environment-specific classes inherit from it
to provide or override values.

"""

import logging
import os

from dotenv import load_dotenv


def load_environment():
    """Loads environment variables based on the MODE environment variable."""
    load_dotenv(dotenv_path=".env")
    mode = os.getenv("MODE", "DEV").upper()
    logging.getLogger("pawprints.config").info("Running in %s mode.", mode)


load_environment()


def get_required_env(name: str) -> str:
    """
    Fetch a required environment variable or raise a clear error.

    Parameters
    ----------
    name : str
        Environment variable name.

    Returns
    -------
    str
        The environment variable's value.

    Raises
    ------
    RuntimeError
        If the variable is unset or empty.
    """
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def int_env(name: str, default: int) -> int:
    """
    Parse an integer environment variable with a default.

    Parameters
    ----------
    name : str
        Environment variable name.
    default : int
        Fallback value.

    Returns
    -------
    int
        Parsed integer (or default on failure).
    """
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


class Config:
    """Base configuration class.

    Loads common environment variables and constructs the database connection URIs.
    Attributes are loaded from the environment upon import.

    Attributes
    ----------
    MODE : str
        The application's running mode (e.g., 'DEV', 'PROD').
    POSTGRES_DB : str
        The name of the database.
    POSTGRES_USER : str
        The username for database access.
    POSTGRES_PASSWORD : str
        The password for database access.
    POSTGRES_HOST : str
        The host for the database server.
    DB_PORT : str
        The port for the database server.
    SQLALCHEMY_DATABASE_URI : str
        The asynchronous database connection string for SQLAlchemy.
    SQLALCHEMY_DATABASE_URI_SYNC : str
        The synchronous database connection string for SQLAlchemy.

    """

    AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "pawcess")
    MODE = os.getenv("MODE", "DEV").upper()
    POSTGRES_DB = get_required_env("POSTGRES_DB")
    POSTGRES_USER = get_required_env("POSTGRES_USER")
    POSTGRES_PASSWORD = get_required_env("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    MINIO_URL = os.getenv("MINIO_URL", "http://minio:9000")
    MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
    DEV_USERNAME = os.getenv("DEV_USERNAME")
    S3USER = os.getenv("MINIO_ROOT_USER")
    S3PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
    # ---- Settings (validated / tunable via env) ----
    SECRET_KEY: str = get_required_env("JWT_SECRET")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Lifetimes (minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int_env(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 5
    )  # 5 hours default
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int_env(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7
    )  # 7 days

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Asynchronous database connection string."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"

    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> str:
        """Synchronous database connection string."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"


class ProdConfig(Config):
    """Production-specific configuration."""

    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")


class DevConfig(Config):
    """Development-specific configuration."""

    POSTGRES_HOST = "localhost"
