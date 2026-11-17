import logging
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from pathlib import Path

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_logger(worker_id: str, level: str = "DEBUG"):
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{worker_id}.log"

    # Create logger (avoid adding multiple handlers)
    logger = logging.getLogger(worker_id)
    if logger.handlers:  # reuse existing logger
        return logger

    logger.setLevel(level)

    # Use concurrent-safe rotating file handler
    handler = ConcurrentTimedRotatingFileHandler(
        log_file,
        when="midnight",      # rotate daily
        backupCount=7,        # keep 7 days
        encoding="utf-8",
        delay=False           # open file immediately
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

 