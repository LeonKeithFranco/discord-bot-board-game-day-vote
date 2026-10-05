from collections.abc import Callable
from datetime import date, datetime, timedelta

import pytest
from pytest_mock import MockerFixture

import src.date
from src.date import (
    TIMEZONE,
    DateCalculator,
    get_all_saturdays_in_month,
    get_target_poll_date,
    get_valid_statutory_holidays_in_month,
)


@pytest.fixture(autouse=True)
def mock_get_today(mocker: MockerFixture) -> None:
    mocker.patch(
        "src.date.get_today", return_value=datetime(2026, 1, 1, tzinfo=TIMEZONE)
    )


@pytest.fixture
def advance_mock_get_today(mocker: MockerFixture) -> Callable[..., None]:
    mock = mocker.patch(
        "src.date.get_today", return_value=datetime(2026, 1, 1, tzinfo=TIMEZONE)
    )

    def advance_a_day() -> None:
        mock.return_value += timedelta(days=1)

    return advance_a_day


class TestDateCalculator:
    def test_date_calc_init(self) -> None:
        first_expected_saturday = date(2026, 1, 3)
        other_expected_first_saturdays = {
            date(2026, 2, 7),
            date(2026, 3, 7),
            date(2026, 4, 4),
            date(2026, 5, 2),
            date(2026, 6, 6),
            date(2026, 7, 4),
            date(2026, 8, 1),
            date(2026, 9, 5),
            date(2026, 10, 3),
            date(2026, 11, 7),
            date(2026, 12, 5),
        }

        date_calc = DateCalculator()

        assert date_calc.target_saturday == first_expected_saturday
        assert len(date_calc._next_saturdays) == 11

        for d in date_calc._next_saturdays:
            assert d.date() in other_expected_first_saturdays

    def test_select_next_saturday(self) -> None:
        other_expected_first_saturdays = [
            date(2026, 2, 7),
            date(2026, 3, 7),
            date(2026, 4, 4),
            date(2026, 5, 2),
            date(2026, 6, 6),
            date(2026, 7, 4),
            date(2026, 8, 1),
            date(2026, 9, 5),
            date(2026, 10, 3),
            date(2026, 11, 7),
            date(2026, 12, 5),
        ]

        date_calc = DateCalculator()

        for i, d in enumerate(other_expected_first_saturdays):
            date_calc.select_next_target_saturday()

            assert date_calc.target_saturday == d
            # 10 because select_next_taret_saturday has already been called once
            assert len(date_calc._next_saturdays) == 10 - i

    def test_get_new_set_of_first_saturdays(
        self, advance_mock_get_today: Callable[..., None]
    ) -> None:
        date_calc = DateCalculator()

        for _ in range(366):
            if src.date.get_today().date() == date_calc.target_saturday:
                date_calc.select_next_target_saturday()
            advance_mock_get_today()

        # same dates because mocked get_today will always return the same date
        first_expected_saturday = date(2027, 1, 2)
        other_expected_first_saturdays = {
            date(2027, 2, 6),
            date(2027, 3, 6),
            date(2027, 4, 3),
            date(2027, 5, 1),
            date(2027, 6, 5),
            date(2027, 7, 3),
            date(2027, 8, 7),
            date(2027, 9, 4),
            date(2027, 10, 2),
            date(2027, 11, 6),
            date(2027, 12, 4),
        }

        assert date_calc.target_saturday == first_expected_saturday

        assert len(date_calc._next_saturdays) == 11
        for d in date_calc._next_saturdays:
            assert d.date() in other_expected_first_saturdays


def test_get_all_saturdays_in_month() -> None:
    all_expected_saturdays = {
        date(2026, 1, 3),
        date(2026, 1, 10),
        date(2026, 1, 17),
        date(2026, 1, 24),
        date(2026, 1, 31),
    }

    for d in get_all_saturdays_in_month(d=date(2026, 1, 1)):
        assert d in all_expected_saturdays


def test_get_valid_statutory_holidays_in_month() -> None:
    # April should return good friday
    holidays = get_valid_statutory_holidays_in_month(d=date(2026, 4, 1))

    assert len(holidays) == 1
    assert holidays[0] == date(2026, 4, 3)

    # September should return the sunday before labour day
    holidays = get_valid_statutory_holidays_in_month(d=date(2026, 9, 1))

    assert len(holidays) == 1
    assert holidays[0] == date(2026, 9, 6)

    # November should return nothing
    holidays = get_valid_statutory_holidays_in_month(d=date(2026, 11, 1))

    assert len(holidays) == 0


def test_get_target_poll_date() -> None:
    assert get_target_poll_date(d=date(2026, 12, 5)) == date(2026, 11, 23)
