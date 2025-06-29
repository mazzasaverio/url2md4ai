"""Logging utilities for url2md4ai."""

import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from ..config import Config


def setup_logger(config: "Config") -> None:
    """Setup loguru logger with configuration."""
    # Remove default handler
    logger.remove()

    # Add console handler with appropriate level and format
    logger.add(
        sys.stdout,
        level=config.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )


def get_logger(name: str):  # type: ignore[no-untyped-def]
    """Get logger instance."""
    return logger.bind(name=name)


def setup_minimal_logger() -> None:
    """Setup minimal logger for basic usage."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<level>{level}</level>: {message}",
        colorize=True,
    )
