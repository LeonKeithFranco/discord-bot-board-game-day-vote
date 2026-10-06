import random
from collections.abc import Iterator
from datetime import date
from pathlib import Path

_TEMPLATE_TOKEN = "{month}"
_FILE_PATH = Path(__file__).resolve().parent.parent / "board_game_poll_titles.txt"

type BoardGameTitle = str


def _get_board_game_poll_titles() -> list[BoardGameTitle]:
    with open(_FILE_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if not line.isspace()]


def _get_random_board_game_poll_title() -> Iterator[BoardGameTitle]:
    titles = _get_board_game_poll_titles()

    while True:
        random.shuffle(titles)
        yield from titles


_titles = _get_random_board_game_poll_title()


def get_random_game_poll_title_with_month(d: date) -> str:
    title = next(_titles)

    return title.replace(_TEMPLATE_TOKEN, d.strftime("%B"))
