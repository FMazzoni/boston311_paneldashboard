"""Logging utilities for the Boston 311 dashboard."""

import logging
import sys

import panel as pn

# Standard logging format
FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


@pn.cache
def get_logger(
    name: str, format_: str = FORMAT, level: int = logging.INFO
) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (usually module name)
        format_: Log message format string
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create and configure handler
    handler = logging.StreamHandler()
    handler.setStream(sys.stdout)
    formatter = logging.Formatter(format_)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    logger.setLevel(level)
    logger.info("Logger successfully configured")
    return logger
