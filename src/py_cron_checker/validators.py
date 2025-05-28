import re
from typing import Sequence

from .exceptions import InvalidCronStructureError


def validate_day_of_month_or_week(
    day_of_month: str | int | None, day_of_week: str | int | None
) -> None:
    """Raise an error if the day of month and day of week are not valid.

    With quartz cron, the day of month and day of week are mutually exclusive.
    If both are set to '?', it is invalid. If both are set to '*', it is invalid.

    One must be set to '?' and the other must be a valid value.

    Args:
        day_of_month: The day of month part of the cron string.
        day_of_week: The day of week part of the cron string.

    Raises:
        InvalidCronStructureError: If the combination is invalid.
    """

    if day_of_month is None or day_of_week is None:
        raise InvalidCronStructureError(
            "day_of_month and day_of_week must not be None."
        )

    day_of_month = str(day_of_month).strip()
    day_of_week = str(day_of_week).strip()

    if day_of_month == "?" and day_of_week == "?":
        raise InvalidCronStructureError(
            "Only one of day-of-month or day-of-week can be '?', not both."
        )

    if day_of_month != "?" and day_of_week != "?":
        raise InvalidCronStructureError(
            "Exactly one of day-of-month or day-of-week must be '?'."
        )

    if day_of_month == "*" and day_of_week != "?":
        raise InvalidCronStructureError(
            "If day-of-month is '*', day-of-week must be '?'."
        )

    if day_of_week == "*" and day_of_month != "?":
        raise InvalidCronStructureError(
            "If day-of-week is '*', day-of-month must be '?'."
        )


def validate_single_digit(part: int, min_value: int, max_value: int) -> bool:
    """
    Validate that a single digit is within the allowed range.

    Args:
        part (int): The integer to validate.
        min_value (int): Minimum valid value.
        max_value (int): Maximum valid value.

    Returns:
        bool: True if valid, False otherwise.
    """
    return min_value <= part <= max_value


def validate_increment(
    base: int, increment: int, min_value: int, max_value: int, increment_max: int
) -> bool:
    """
    Validate that an increment expression is valid.

    Args:
        base (int): The base value (e.g. from '5/10').
        increment (int): The increment value.
        min_value (int): Minimum valid base value.
        max_value (int): Maximum valid base value.
        increment_max (int): Maximum allowed increment.

    Returns:
        bool: True if valid, False otherwise.
    """
    return min_value <= base <= max_value and 1 <= increment <= increment_max


def validate_range(start: int, end: int, min_value: int, max_value: int) -> bool:
    """
    Validate a numeric range.

    Args:
        start (int): Start of the range.
        end (int): End of the range.
        min_value (int): Minimum allowed value.
        max_value (int): Maximum allowed value.

    Returns:
        bool: True if both start and end are within bounds, False otherwise.
    """
    return min_value <= start <= max_value and min_value <= end <= max_value


def validate_range_with_increment(
    start: int, end: int, increment: int, min_value: int, max_value: int
) -> bool:
    """
    Validate a range with increment, e.g., '1-5/2'.

    Args:
        start (int): Start of the range.
        end (int): End of the range.
        increment (int): Step size.
        min_value (int): Minimum allowed value.
        max_value (int): Maximum allowed value.

    Returns:
        bool: True if all components are valid, False otherwise.
    """
    return (
        min_value <= start <= max_value
        and min_value <= end <= max_value
        and 1 <= increment <= (max_value - min_value + 1)
    )


def validate_specifics(
    values: list[str], valid_int_range: range, allowed_literals: set[str]
) -> bool:
    """
    Validate a list of specific values.

    Args:
        values (list[str]): The specific values, e.g. ['1', '2', '3'].
        valid_int_range (range): Allowed numeric values.
        allowed_literals (set[str]): Allowed non-numeric literals.

    Returns:
        bool: True if all values are valid, False otherwise.
    """
    if all(v.isdigit() for v in values):
        return all(int(v) in valid_int_range for v in values)
    return all(v in allowed_literals for v in values)


def validate_patterns(part: str, patterns: Sequence[re.Pattern]) -> bool:
    """
    Validate a part using regular expressions.

    Args:
        part (str): The cron field to validate.
        patterns (Sequence[re.Pattern]): A list of regex patterns.

    Returns:
        bool: True if any pattern matches, False otherwise.
    """
    if part is None:
        return False
    return any(p.match(part) for p in patterns)
