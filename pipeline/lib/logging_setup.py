"""Structured logging configuration for the pipeline."""
import logging
import sys

from pipeline.config import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Return a logger with consistent formatting.

    Usage:
        from pipeline.lib.logging_setup import get_logger
        log = get_logger("reddit_recent")
    """
    logger = logging.getLogger(f"fullcarts.pipeline.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    return logger
