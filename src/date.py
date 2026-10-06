from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import holidays
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, SA, WEEKLY, rrule

TIMEZONE = ZoneInfo("America/Vancouver")
# the monday of the previous week of the first saturday of the month
N_DAYS_BEFORE_FIRST_SATURDAY_FOR_POLL = relativedelta(days=-12)
RUN_TIME = time(hour=12, minute=0, tzinfo=TIMEZONE)


def get_today() -> datetime:
    return datetime.now(tz=TIMEZONE)


class DateCalculator:
    """For keeping track of the first saturday of every month.

    Calculates the next 12 first Saturdays and then keeps track of the next target Saturday.
    """

    _next_saturdays: list[datetime]
    target_saturday: date

    def __init__(self) -> None:
        self._next_saturdays = self._generate_saturdays(get_today().date())
        self.select_next_target_saturday()

    def _generate_saturdays(self, start: date) -> list[datetime]:
        return list(rrule(MONTHLY, byweekday=SA(1), dtstart=start, count=12))

    def _get_next_target_saturday(self) -> date:
        if not self._next_saturdays:
            self._next_saturdays = self._generate_saturdays(
                self.target_saturday + relativedelta(days=1)
            )

        return self._next_saturdays.pop(0).date()

    def select_next_target_saturday(self) -> None:
        self.target_saturday = self._get_next_target_saturday()


date_calc = DateCalculator()


def advance_date_calc_to_valid_state() -> None:
    is_after_poll_day = get_today().date() > get_target_poll_date(
        date_calc.target_saturday
    )
    is_poll_day_and_past_target_time = (
        get_today().date() == get_target_poll_date(date_calc.target_saturday)
    ) and (get_today().time() > RUN_TIME)

    if is_after_poll_day or is_poll_day_and_past_target_time:
        date_calc.select_next_target_saturday()


def get_all_saturdays_in_month(d: date) -> list[date]:
    first_day = d.replace(day=1)
    last_day = d + relativedelta(day=31)

    return [
        dt.date()
        for dt in rrule(WEEKLY, byweekday=SA, dtstart=first_day, until=last_day)
    ]


def get_valid_statutory_holidays_in_month(d: date) -> list[date]:
    """Returns the days around BC statutory holidays that can be voted on in d's month.

    A holiday on a Friday is returned as is. A holiday on a Monday returns the Sunday
    before it instead, as long as that Sunday is in d's month. If the 1st of the next
    month is a Monday holiday, the last day of d's month is also returned. Holidays on
    any other day are ignored. d can be any date in the month.
    """
    bc_holidays = holidays.Canada(subdiv="BC", years=d.year)

    valid_holidays_this_month: list[date] = []

    for day in bc_holidays:
        if day.month != d.month:
            continue

        match day.isoweekday():
            case 1:
                valid_holidays_this_month.append(day - relativedelta(days=1))
            case 5:
                valid_holidays_this_month.append(day)

    # if monday is the first of the month, the sunday of the previous month will be added
    # and then need to be filtered out
    valid_holidays_this_month = [
        day for day in valid_holidays_this_month if day.month == d.month
    ]

    # if the start of the next month is a monday, the sunday before should be added
    eom = d + relativedelta(day=31)
    day_after_eom = eom + relativedelta(days=1)
    if day_after_eom in bc_holidays and day_after_eom.isoweekday() == 1:
        valid_holidays_this_month.append(eom)

    return valid_holidays_this_month


def get_all_valid_days_in_month(d: date) -> list[date]:
    valid_days = get_all_saturdays_in_month(d) + get_valid_statutory_holidays_in_month(
        d
    )

    return sorted(valid_days)


def get_target_poll_date(d: date) -> date:
    return d + N_DAYS_BEFORE_FIRST_SATURDAY_FOR_POLL


if __name__ == "__main__":
    date_calc = DateCalculator()
    print(date_calc._next_saturdays)
    print(date_calc.target_saturday)
    today = get_today()
    print(get_all_saturdays_in_month(today.date()))
    print(get_valid_statutory_holidays_in_month(today.date()))
