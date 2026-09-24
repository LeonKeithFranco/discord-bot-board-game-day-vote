from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from dateutil.rrule import MONTHLY, SA, rrule
from dateutil.utils import today

RUN_TIME = time(hour=12, minute=0, tzinfo=ZoneInfo("America/Vancouver"))


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
        return list(rrule(MONTHLY, byweekday=SA(1), dtstart=today(), count=12))

    def _get_next_target_saturday(self) -> date:
        if not self._next_saturdays:
            self._next_saturdays = self._generate_saturdays()

        return self._next_saturdays.pop(0).date()

    def select_next_target_saturday(self) -> None:
        self.target_saturday = self._get_next_target_saturday()


if __name__ == "__main__":
    date_calc = DateCalculator()
    print(date_calc._next_saturdays)
    print(date_calc.target_saturday)
