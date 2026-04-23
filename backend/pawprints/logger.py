import logging
from logging.config import dictConfig
import os


def _log_level() -> str:
    return os.environ.get("LOG_LEVEL", "INFO").upper()


class LogConfig:
    """Logging configuration to be set for the FastAPI app."""

    LOGGER_NAME: str = "pawprints"
    SYSTEM_NAME: str = "PAWPRINTS-API"
    LOG_FORMAT: str = f"{SYSTEM_NAME} %(asctime)s: %(levelname)s - %(name)s - %(message)s"

    @classmethod
    def build(cls) -> dict:
        level = _log_level()
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": cls.LOG_FORMAT,
                    "datefmt": "%H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                cls.LOGGER_NAME: {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
            },
        }


def setup_logging():
    """Run during app startup to apply the config."""
    dictConfig(LogConfig.build())


def get_logger() -> logging.Logger:
    """FastAPI Dependency: returns the configured logger."""
    return logging.getLogger(LogConfig.LOGGER_NAME)
