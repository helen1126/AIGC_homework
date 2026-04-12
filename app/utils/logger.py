import logging
import sys
from typing import Optional

from app.config import get_config


_logger: Optional[logging.Logger] = None


def setup_logger() -> logging.Logger:
    global _logger
    config = get_config()
    logger = logging.getLogger("sd_api")
    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if config.logging.file:
        file_handler = logging.FileHandler(
            config.logging.file, encoding="utf-8", mode="a"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger
