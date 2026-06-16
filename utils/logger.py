"""Logging utility"""
import logging
import os
from datetime import datetime

class Logger:
    """Custom logger for the application"""
    
    _loggers = {}
    _log_dir = "logs"
    
    def __new__(cls, name):
        if name not in cls._loggers:
            # Create logs directory if it doesn't exist
            if not os.path.exists(cls._log_dir):
                os.makedirs(cls._log_dir)
            
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            log_file = os.path.join(cls._log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]
