"""
Logging Configuration for Orgaplex-Analyzer Software

This module provides centralized logging configuration for all modules.

Author: Philipp Kaintoch
Date: 2025-11-18
Version: 2.2.0
"""

import logging
import sys


def setup_logger(name: str, level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Parameters:
    -----------
    name : str
        Logger name (typically __name__ of the calling module)
    level : str
        Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    log_file : str, optional
        If provided, also log to this file

    Returns:
    --------
    logging.Logger : Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Format: [LEVEL] message (streamlined for readability)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # More detailed format for file logs
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.

    Parameters:
    -----------
    name : str
        Logger name

    Returns:
    --------
    logging.Logger : Logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger = setup_logger(name)

    return logger
