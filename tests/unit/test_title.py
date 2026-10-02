from src.date import get_today
from src.title import (
    _TEMPLATE_TOKEN,
    _get_board_game_poll_titles,
    get_random_game_poll_title_with_month,
)


def test_get_board_game_titles() -> None:
    titles = _get_board_game_poll_titles()

    assert len(titles) >= 1

    for title in titles:
        assert _TEMPLATE_TOKEN in title


def test_get_random_game_poll_title_with_month() -> None:
    today = get_today()
    month_str = today.strftime("%B")

    title = get_random_game_poll_title_with_month(today)

    assert _TEMPLATE_TOKEN not in title
    assert month_str in title
