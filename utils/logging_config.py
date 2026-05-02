import logging
import sys


def configure_logger(level: int = logging.INFO) -> None:
    """Configure the root logger with a StreamHandler.

    Timestamps and log rotation are handled by Docker, so only a
    StreamHandler writing to stdout is needed here.
    """
    formatter = logging.Formatter("[%(name)s] [%(levelname)s] %(message)s")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)

    if not root.handlers:
        root.addHandler(handler)
