import logging

from src.config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)-8s %(name)s::%(funcName)s: %(message)s",
    )
