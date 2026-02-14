"""
日志工具
"""
import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str = "VictoryQuant", 
                log_file: Optional[str] = None,
                level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "VictoryQuant") -> logging.Logger:
    return logging.getLogger(name)


default_logger = setup_logger(
    "VictoryQuant",
    log_file=f"logs/victoryquant_{datetime.now().strftime('%Y%m%d')}.log"
)
