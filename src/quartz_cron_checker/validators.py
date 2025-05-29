import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from logging import getLogger

from .constants import (
    DOW_OCCURRENCE_PATTERN,
    DOW_RANGE_PATTERN,
    INCREMENT_PATTERN,
    LAST_DOW_IN_MONTH_PATTERN,
    LAST_N_DAYS_OF_MONTH_PATTERN,
    LIST_OF_DIGITS_PATTERN,
    LIST_OF_STRINGS_PATTERN,
    MONTH_RANGE_PATTERN,
    NEAREST_WEEKDAY_DAY_OF_MONTH_PATTERN,
    RANGE_PATTERN,
    RANGE_WITH_INCREMENT_PATTERN,
    SINGLE_LITERAL_PATTERN,
    SPECIFIC_DOW_PATTERN,
    SPECIFIC_MONTH_PATTERN,
    WILDCARD_PATTERN,
)
from .exceptions import InvalidCronStructureError

LOGGER = getLogger(__name__)


@dataclass
class PatternValidator:
    """Handle validation of a cron part against a regex pattern and a validator function."""

    description: str
    pattern: re.Pattern
    validator: Callable[[str], bool] | None = None
    failure_hint: str | None = None

    def validate(self, part: str) -> tuple[bool, bool]:
        """Validate a part against the pattern and optional validator.

        Args:
            part (str): The cron field to validate.

        Returns:
            tuple[bool,bool]: A tuple where the first element indicates if the part matches the pattern,
            and the second element indicates if the part passes the optional validator.
        """
        if not self.pattern.match(part):
            LOGGER.debug(
                "Pattern for %r ('%s') did not match for part: %r", self.description, self.pattern.pattern, part
            )
            return False, False

        LOGGER.debug("Pattern for %r ('%s') matched for part: %r", self.description, self.pattern.pattern, part)

        if self.validator is None:
            LOGGER.debug("No validator for %r, returning True", self.description)
            return True, True

        match = self.pattern.match(part)
        assert match is not None, "Pattern match should not return None"

        matched_value = match.groups()[0]
        LOGGER.debug("Extracted value from part %r: %r", part, matched_value)

        if self.validator is None or self.validator(matched_value):
            return True, True

        LOGGER.debug("Validator for %r failed for part: %r", self.description, part)
        return True, False


LAST_N_DAYS_OF_MONTH_VALIDATOR = PatternValidator(
    description="Last N days of month",
    pattern=LAST_N_DAYS_OF_MONTH_PATTERN,
    validator=lambda part: 1 <= int(part) <= 30,
    failure_hint="must be between 1 and 30",
)

NEAREST_WEEKDAY_VALIDATOR = PatternValidator(
    description="Nearest weekday",
    pattern=NEAREST_WEEKDAY_DAY_OF_MONTH_PATTERN,
    validator=lambda part: 1 <= int(part) <= 31,
    failure_hint="must be between 1 and 31",
)


SINGLE_LITERAL_VALIDATOR = PatternValidator(description="Single literal", pattern=SINGLE_LITERAL_PATTERN)
WILDCARD_VALIDATOR = PatternValidator(description="Wildcard", pattern=WILDCARD_PATTERN)
RANGE_VALIDATOR = PatternValidator(description="Range", pattern=RANGE_PATTERN)
INCREMENT_VALIDATOR = PatternValidator(description="Increment", pattern=INCREMENT_PATTERN)
RANGE_WITH_INCREMENT_VALIDATOR = PatternValidator(
    description="Range with increment", pattern=RANGE_WITH_INCREMENT_PATTERN
)
LIST_OF_DIGITS_VALIDATOR = PatternValidator(description="List of digits", pattern=LIST_OF_DIGITS_PATTERN)
LIST_OF_STRINGS_VALIDATOR = PatternValidator(description="List of strings", pattern=LIST_OF_STRINGS_PATTERN)
DOW_OCCURRENCE_VALIDATOR = PatternValidator(description="Day of week occurrence", pattern=DOW_OCCURRENCE_PATTERN)
LAST_DOW_IN_MONTH_VALIDATOR = PatternValidator(
    description="Last day of week in month", pattern=LAST_DOW_IN_MONTH_PATTERN
)
DOW_RANGE_VALIDATOR = PatternValidator(description="Day of week range", pattern=DOW_RANGE_PATTERN)
SPECIFIC_DOW_VALIDATOR = PatternValidator(description="Specific day of week", pattern=SPECIFIC_DOW_PATTERN)
MONTH_RANGE_VALIDATOR = PatternValidator(description="Month range", pattern=MONTH_RANGE_PATTERN)
SPECIFIC_MONTH_VALIDATOR = PatternValidator(description="Specific month", pattern=SPECIFIC_MONTH_PATTERN)


DEFAULT_NUMERIC_VALIDATORS = (
    RANGE_VALIDATOR,
    INCREMENT_VALIDATOR,
    RANGE_WITH_INCREMENT_VALIDATOR,
    LIST_OF_DIGITS_VALIDATOR,
)


def validate_day_of_month_or_week(day_of_month: str | int | None, day_of_week: str | int | None) -> None:
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
        raise InvalidCronStructureError("day_of_month and day_of_week must not be None.")

    day_of_month = str(day_of_month).strip()
    day_of_week = str(day_of_week).strip()

    if day_of_month == "?" and day_of_week == "?":
        raise InvalidCronStructureError("Only one of day-of-month or day-of-week can be '?', not both.")

    if day_of_month != "?" and day_of_week != "?":
        raise InvalidCronStructureError("Exactly one of day-of-month or day-of-week must be '?'.")

    if day_of_month == "*" and day_of_week != "?":
        raise InvalidCronStructureError("If day-of-month is '*', day-of-week must be '?'.")

    if day_of_week == "*" and day_of_month != "?":
        raise InvalidCronStructureError("If day-of-week is '*', day-of-month must be '?'.")


def validate_single_digit(part: int, min_value: int, max_value: int) -> bool:
    """Validate that a single digit is within the allowed range.

    Args:
        part (int): The integer to validate.
        min_value (int): Minimum valid value.
        max_value (int): Maximum valid value.

    Returns:
        bool: True if valid, False otherwise.
    """
    return min_value <= part <= max_value


def validate_increment(base: int, increment: int, min_value: int, max_value: int, increment_max: int) -> bool:
    """Validate that an increment expression is valid.

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
    """Validate a numeric range.

    Args:
        start (int): Start of the range.
        end (int): End of the range.
        min_value (int): Minimum allowed value.
        max_value (int): Maximum allowed value.

    Returns:
        bool: True if both start and end are within bounds, False otherwise.
    """
    return min_value <= start <= max_value and min_value <= end <= max_value


def validate_range_with_increment(start: int, end: int, increment: int, min_value: int, max_value: int) -> bool:
    """Validate a range with increment, e.g., '1-5/2'.

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


def validate_specifics(values: list[str], valid_int_range: range, allowed_literals: set[str]) -> bool:
    """Validate a list of specific values.

    Args:
        values (list[str]): The specific values, e.g. ['1', '2', '3'].
        valid_int_range (range): Allowed numeric values.
        allowed_literals (set[str]): Allowed non-numeric literals.

    Returns:
        bool: True if all values are valid, False otherwise.
    """
    if all(v.isdigit() for v in values):
        return all(int(v) in valid_int_range for v in values)
    return all(validate_literals(v, allowed_literals) for v in values)


def validate_patterns(part: str, patterns: Sequence[re.Pattern]) -> bool:
    """Validate a part using regular expressions.

    Args:
        part (str): The cron field to validate.
        patterns (Sequence[re.Pattern]): A list of regex patterns.

    Returns:
        bool: True if any pattern matches, False otherwise.
    """
    if part is None:
        return False

    for p in patterns:
        if p.match(part):
            LOGGER.debug("Pattern matched: '%s' for part: %r", p.pattern, part)
            return True

    return False


def validate_literals(part: str, literals: set[str]) -> bool:
    """Validate a part against a set of allowed literals.

    Args:
        part (str): The cron field to validate.
        literals (set[str]): A set of allowed literal values.

    Returns:
        bool: True if the part is in the set of literals, False otherwise.
    """
    if part is None:
        return False

    lcase_literals = {lit.lower() for lit in literals}

    if part.lower() in lcase_literals:
        LOGGER.debug("Literal matched: %r", part)
        return True

    return False
