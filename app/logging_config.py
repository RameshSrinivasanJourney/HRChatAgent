import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def configure_logging():

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)