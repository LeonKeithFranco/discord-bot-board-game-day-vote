from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import holidays
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, SA, WEEKLY, rrule

TIMEZONE = ZoneInfo("America/Vancouver")
RUN_TIME = time(hour=12, minute=0, tzinfo=TIMEZONE)
_TODAY = datetime.now(tz=TIMEZONE)


class DateCalculator:
    """For keeping track of the first saturday of every month.

    Calculates the next 12 first Saturdays and then keeps track of the next target Saturday.
    """

    _next_saturdays: list[datetime]
    target_saturday: date

    def __init__(self) -> None:
        self._next_saturdays = self._generate_saturdays()
        self.select_next_target_saturday()

    def _generate_saturdays(self) -> list[datetime]:
        return list(rrule(MONTHLY, byweekday=SA(1), dtstart=_TODAY, count=12))

    def _get_next_target_saturday(self) -> date:
        if not self._next_saturdays:
            self._next_saturdays = self._generate_saturdays()

        return self._next_saturdays.pop(0).date()

    def select_next_target_saturday(self) -> None:
        self.target_saturday = self._get_next_target_saturday()


def get_all_saturdays_in_month(d: date) -> list[date]:
    first_day = d.replace(day=1)
    last_day = d + relativedelta(day=31)

    return [
        dt.date()
        for dt in rrule(WEEKLY, byweekday=SA, dtstart=first_day, until=last_day)
    ]


def get_valid_statutory_holidays_in_month(d: date) -> list[date]:
    """Returns the dates that are valid relative to staturoy holiday dates.

    If holiday dates land a Friday, it is returned. If it lands on a Monday, the Sunday
    previous is returned instead. Any other days are discarded.
    """
    bc_holidays = holidays.Canada(subdiv="BC", years=_TODAY.year)

    valid_holidays_this_month: list[date] = []

    for day in bc_holidays:
        if day.month != d.month:
            continue

        match day.isoweekday():
            case 1:
                valid_holidays_this_month.append(day - relativedelta(days=1))
            case 5:
                valid_holidays_this_month.append(day)

    return valid_holidays_this_month


if __name__ == "__main__":
    date_calc = DateCalculator()
    print(date_calc._next_saturdays)
    print(date_calc.target_saturday)
    print(get_all_saturdays_in_month(_TODAY.date()))
    print(get_valid_statutory_holidays_in_month(_TODAY.date()))
