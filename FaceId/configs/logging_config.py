"""
configs/logging_config.py
--------------------------
Central logging configuration for FacePass AiService.
Call ``setup_logging()`` once at application startup (in main.py lifespan).

Features:
  - Structured, levelled console output with timestamp and module name
  - Rotating file handler → logs/facepass.log
  - Log level and file path driven by Settings
"""

import logging
import logging.handlers
from pathlib import Path

from configs.settings import settings


def setup_logging() -> None:
    """Configure root logger with console + rotating file handlers."""

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # ── Console handler ─────────────────────────────────────────────────────
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(fmt)

    # ── Rotating file handler (10 MB × 5 backups) ───────────────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # always capture DEBUG in file
    file_handler.setFormatter(fmt)

    # ── Root logger ─────────────────────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console)
    root.addHandler(file_handler)

    # Silence overly verbose third-party loggers
    for noisy in ("ultralytics", "insightface", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialised — level=%s  file=%s", settings.log_level, log_path
    )


def get_logger(name: str) -> logging.Logger:
    """Convenience wrapper — modules call ``get_logger(__name__)``."""
    return logging.getLogger(name)
