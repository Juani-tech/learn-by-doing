"""Logging configuration."""
import logging
import sys
from app.config import get_settings


def setup_logging():
    """Configure structured logging."""
    settings = get_settings()
    
    # Create logger
    logger = logging.getLogger("learnbydoing")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()
