"""
Logging setup for Module A
Configures both console and file logging with rotation
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from .config import (
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE,
    LOG_FILE_MAX_BYTES,
    LOG_FILE_BACKUP_COUNT
)


def setup_logging(module_name: str = "module_a") -> logging.Logger:
    """
    Set up logging with both console and file handlers
    
    Args:
        module_name: Name of the module (for logger name)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if LOG_FILE:
        try:
            # Ensure log directory exists
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_FILE_MAX_BYTES,
                backupCount=LOG_FILE_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {LOG_FILE}")
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")
    
    return logger


def get_pinecone_logger() -> logging.Logger:
    """
    Get a logger specifically for Pinecone operations
    
    Returns:
        Logger instance for Pinecone operations
    """
    logger = logging.getLogger("module_a.pinecone")
    
    # If logger doesn't have handlers, set them up
    if not logger.handlers:
        # Use parent logger's handlers
        parent_logger = logging.getLogger("module_a")
        if not parent_logger.handlers:
            setup_logging("module_a")
        
        # Copy handlers from parent
        for handler in logging.getLogger("module_a").handlers:
            logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    return logger
