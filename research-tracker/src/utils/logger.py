"""Logging configuration"""

import sys
from pathlib import Path
from loguru import logger
from ..config.settings import Settings


def setup_logger(name: str = "research-tracker") -> logger:
    """
    Set up logger with file and console output
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Remove default logger
    logger.remove()
    
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=Settings.LOG_LEVEL,
        colorize=True
    )
    
    # File output
    log_file = Settings.LOG_DIR / f"{name}.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=Settings.LOG_LEVEL,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    return logger
