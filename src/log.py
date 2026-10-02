import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config import settings

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "app.log"


def setup_logging() -> None:
    LOG_PATH.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)-8s %(name)s::%(funcName)s: %(message)s",
        handlers=[
            StreamHandler(),
            RotatingFileHandler(
                LOG_PATH,
                maxBytes=1_000_000,
                backupCount=5,
                encoding="utf-8",
            ),
        ],
    )
