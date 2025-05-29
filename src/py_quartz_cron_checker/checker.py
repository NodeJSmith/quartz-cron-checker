from typing import Literal

import attrs

from py_quartz_cron_checker.exceptions import InvalidCronStructureError
from py_quartz_cron_checker.validators import validate_day_of_month_or_week

from .config import (
    DAY_OF_MONTH_CONFIG,
    DAY_OF_WEEK_CONFIG,
    HOUR_CONFIG,
    MINUTE_CONFIG,
    MONTH_CONFIG,
    SECOND_CONFIG,
    YEAR_CONFIG,
)

CRON_TEMPLATE_NO_YEAR = "{second} {minute} {hour} {day_of_month} {month} {day_of_week}"
CRON_TEMPLATE = CRON_TEMPLATE_NO_YEAR + " {year}"
REQUIRED_PARTS = ["second", "minute", "hour", "day_of_month", "month", "day_of_week"]


@attrs.define
class QuartzCronChecker:
    second: str
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str
    year: str | None = None
    cron_string: str | None = None

    def __attrs_post_init__(self):
        self.second = self.second.replace(" ", "")
        self.minute = self.minute.replace(" ", "")
        self.hour = self.hour.replace(" ", "")
        self.day_of_month = self.day_of_month.replace(" ", "")
        self.month = self.month.replace(" ", "")
        self.day_of_week = self.day_of_week.replace(" ", "")
        self.year = self.year.replace(" ", "") if self.year else None

    def __repr__(self) -> str:
        return f"<CronStr {str(self)}>"

    def __str__(self) -> str:
        parts = {
            "second": self.second,
            "minute": self.minute,
            "hour": self.hour,
            "day_of_month": self.day_of_month,
            "month": self.month,
            "day_of_week": self.day_of_week,
        }

        if self.year is not None:
            parts["year"] = self.year
            return CRON_TEMPLATE.format(**parts)

        return CRON_TEMPLATE_NO_YEAR.format(**parts)

    def validate(self) -> Literal[True]:
        """
        Validate the cron string by:

        1. Ensuring required parts are present.
        2. Checking mutual exclusivity of day_of_month and day_of_week.
        3. Validating each part using its corresponding field config.
        """

        if not all(getattr(self, part) for part in REQUIRED_PARTS):
            missing_parts = [part for part in REQUIRED_PARTS if not getattr(self, part)]
            raise InvalidCronStructureError(
                f"Missing required parts in cron string: {', '.join(missing_parts)}"
            )

        validate_day_of_month_or_week(self.day_of_month, self.day_of_week)

        for config, value in [
            (SECOND_CONFIG, self.second),
            (MINUTE_CONFIG, self.minute),
            (HOUR_CONFIG, self.hour),
            (DAY_OF_MONTH_CONFIG, self.day_of_month),
            (MONTH_CONFIG, self.month),
            (DAY_OF_WEEK_CONFIG, self.day_of_week),
        ]:
            config.validate(value)

        if self.year:
            YEAR_CONFIG.validate(self.year)

        return True

    @classmethod
    def from_cron_string(cls, cron_str: str):
        """Convert a cron string to a CronStr object.

        Args:
            cron_str (str): The cron string to convert.

        Returns:
            CronStr: A CronStr object with the converted values.
        """
        cron_parts = cron_str.strip().split(" ")
        if len(cron_parts) == 6:
            # this slightly weird looking syntax makes the type checker happy
            # we add a None for the year part, since it's not present in 6-part cron strings
            return cls(*[*cron_parts, None], cron_string=cron_str)
        if len(cron_parts) == 7:
            return cls(*cron_parts, cron_string=cron_str)

        raise InvalidCronStructureError(
            f"Invalid cron string: {cron_str}. Expected 6 or 7 parts, got {len(cron_parts)}."
        )

    @staticmethod
    def validate_cron_string(cron_str: str) -> bool:
        """Validate a cron string.

        Args:
            cron_str (str): The cron string to validate.

        Returns:
            bool: True if the cron string is valid, False otherwise.
        """
        cron = QuartzCronChecker.from_cron_string(cron_str)
        cron.validate()
        return True
