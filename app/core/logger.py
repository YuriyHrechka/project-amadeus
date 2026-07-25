import logging
import sys

from app.core.config import settings

_FORMATTER = logging.Formatter(
    # Dry and structured format: [Time] - [Module Name] - [Level] - Message
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s - [LINE:%(lineno)d]#",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Loggers handed out so far, so a run log started later still reaches all of them.
_loggers: dict[str, logging.Logger] = {}
_run_handler: logging.FileHandler | None = None


def init_logger(name: str) -> logging.Logger:
    """
    Initialize and configure a standard logger.

    :param name: The name of the logger, typically the __name__ of the calling module.
    :return: A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers if the logger is initialized multiple times
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(settings.LOG_LEVEL)
        handler.setFormatter(_FORMATTER)
        logger.addHandler(handler)

        # Disable propagation to avoid duplicate log entries
        logger.propagate = False

    # A run log opened earlier applies to loggers created afterwards too.
    if _run_handler is not None and _run_handler not in logger.handlers:
        logger.addHandler(_run_handler)

    _loggers[name] = logger
    return logger
