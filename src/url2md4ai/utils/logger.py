"""Logging utilities for url2md4ai."""

import sys

from loguru import logger


def setup_logger(config) -> None:
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


def get_logger(name: str):
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
