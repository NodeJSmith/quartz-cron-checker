from dataclasses import dataclass
from typing import Literal

from quartz_cron_checker.exceptions import InvalidCronStructureError
from quartz_cron_checker.validators import validate_day_of_month_or_week

from .field_configs import (
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


@dataclass
class QuartzCronChecker:
    second: str
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str
    year: str | None = None
    cron_string: str | None = None

    def __post_init__(self):
        self.second = self.second.replace(" ", "")
        self.minute = self.minute.replace(" ", "")
        self.hour = self.hour.replace(" ", "")
        self.day_of_month = self.day_of_month.replace(" ", "")
        self.month = self.month.replace(" ", "")
        self.day_of_week = self.day_of_week.replace(" ", "")
        self.year = self.year.replace(" ", "") if self.year else None

    def __repr__(self) -> str:
        return f"<QuartzCronChecker {self!s}>"

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
        """Validate the cron string.

        This method performs the following checks:
            1. Ensuring required parts are present.
            2. Checking mutual exclusivity of day_of_month and day_of_week.
            3. Validating each part using its corresponding field config.

        Raises:
            InvalidCronStructureError: If the cron string is missing required parts or has invalid structure.
            InvalidCronPartError: If any part of the cron string is invalid.
            ValueOutOfBoundsError: If any part of the cron string is out of bounds.
            IncrementOutOfBoundsError: If an increment value is out of bounds.
            RangeOutOfBoundsError: If a range is out of bounds.
            RangeIncrementOutOfBoundsError: If a range with increment is out of bounds.
            SpecificsOutOfBoundsError: If specific values are out of bounds.

        Returns:
            Literal[True]: Returns True if the cron string is valid.
        """
        if not all(getattr(self, part) for part in REQUIRED_PARTS):
            missing_parts = [part for part in REQUIRED_PARTS if not getattr(self, part)]
            raise InvalidCronStructureError(f"Missing required parts in cron string: {', '.join(missing_parts)}")

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
    def from_cron_string(cls, cron_str: str) -> "QuartzCronChecker":
        """Convert a cron string to a QuartzCronChecker object.

        Args:
            cron_str (str): The cron string to convert.

        Returns:
            QuartzCronChecker: A QuartzCronChecker object with the converted values.
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
    def validate_cron_string(cron_str: str) -> Literal[True]:
        """Validate a cron string.

        Args:
            cron_str (str): The cron string to validate.

        Returns:
            Literal[True]: Returns True if the cron string is valid.

        Raises:
            InvalidCronStructureError: If the cron string is invalid.
            InvalidCronPartError: If any part of the cron string is invalid.
            ValueOutOfBoundsError: If any part of the cron string is out of bounds.
            IncrementOutOfBoundsError: If an increment value is out of bounds.
            RangeOutOfBoundsError: If a range is out of bounds.
            RangeIncrementOutOfBoundsError: If a range with increment is out of bounds.
            SpecificsOutOfBoundsError: If specific values are out of bounds.
        """
        cron = QuartzCronChecker.from_cron_string(cron_str)
        cron.validate()
        return True


def validate_second(part: str) -> Literal[True]:
    """Validate the 'second' part of a cron string.

    Args:
        part (str): The 'second' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the 'second' part is invalid - exact error depends on the specific validation failure.
    """
    return SECOND_CONFIG.validate(part)


def validate_minute(part: str) -> Literal[True]:
    """Validate the 'minute' part of a cron string.

    Args:
        part (str): The 'minute' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the part is invalid - exact error depends on the specific validation failure.
    """
    return MINUTE_CONFIG.validate(part)


def validate_hour(part: str) -> Literal[True]:
    """Validate the 'hour' part of a cron string.

    Args:
        part (str): The 'hour' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the part is invalid - exact error depends on the specific validation failure.
    """
    return HOUR_CONFIG.validate(part)


def validate_day_of_month(part: str) -> Literal[True]:
    """Validate the 'day_of_month' part of a cron string.

    Args:
        part (str): The 'day_of_month' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the part is invalid - exact error depends on the specific validation failure.
    """
    return DAY_OF_MONTH_CONFIG.validate(part)


def validate_month(part: str) -> Literal[True]:
    """Validate the 'month' part of a cron string.

    Args:
        part (str): The 'month' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the part is invalid - exact error depends on the specific validation failure.
    """
    return MONTH_CONFIG.validate(part)


def validate_day_of_week(part: str) -> Literal[True]:
    """Validate the 'day_of_week' part of a cron string.

    Args:
        part (str): The 'day_of_week' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the part is invalid - exact error depends on the specific validation failure.
    """
    return DAY_OF_WEEK_CONFIG.validate(part)


def validate_year(part: str) -> Literal[True]:
    """Validate the 'year' part of a cron string.

    Args:
        part (str): The 'year' part of the cron string to validate.

    Returns:
        Literal[True]: Returns True if validation is successful.

    Raises:
        InvalidCronPartError: If the part is invalid - exact error depends on the specific validation failure.
    """
    return YEAR_CONFIG.validate(part)


def validate_cron_string(cron_str: str) -> Literal[True]:
    """Validate a cron string.

    Args:
        cron_str (str): The cron string to validate.

    Returns:
        Literal[True]: Returns True if the cron string is valid.

    Raises:
        InvalidCronStructureError: If the cron string is invalid.
        InvalidCronPartError: If any part of the cron string is invalid.
        ValueOutOfBoundsError: If any part of the cron string is out of bounds.
        IncrementOutOfBoundsError: If an increment value is out of bounds.
        RangeOutOfBoundsError: If a range is out of bounds.
        RangeIncrementOutOfBoundsError: If a range with increment is out of bounds.
        SpecificsOutOfBoundsError: If specific values are out of bounds.
    """
    return QuartzCronChecker.validate_cron_string(cron_str)
