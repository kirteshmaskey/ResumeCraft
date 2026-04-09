"""
Structured logging configuration.
- Format: timestamp :: level - function_name :: message
- Daily rotation with 7-day retention
- Separate log files per service module
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from app.core.config import get_settings

settings = get_settings()

# ── Log Format ───────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s :: %(levelname)s - %(funcName)s :: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ── Service Log Files ────────────────────────────────────────────────────
SERVICE_LOGGERS = [
    "auth",
    "app",  # General application logger
]


def setup_logging() -> None:
    """
    Initialize structured logging with daily rotation.
    Creates separate log files for each service module.
    """
    log_dir = settings.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    for service_name in SERVICE_LOGGERS:
        logger = logging.getLogger(service_name)
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        logger.propagate = False

        # Skip if handlers already configured (avoid duplicates on reload)
        if logger.handlers:
            continue

        # File handler with daily rotation
        log_file = os.path.join(log_dir, f"{service_name}.log")
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=settings.LOG_RETENTION_DAYS,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"
        logger.addHandler(file_handler)

        # Console handler (for dev)
        if settings.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)


def get_logger(service_name: str) -> logging.Logger:
    """
    Get a service-specific logger.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger("auth")
        logger.info("User login successful", extra={"user_id": "123"})
    """
    if service_name not in SERVICE_LOGGERS:
        service_name = "app"
    return logging.getLogger(service_name)
