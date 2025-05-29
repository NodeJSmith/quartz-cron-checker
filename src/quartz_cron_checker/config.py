import re

import attrs

from quartz_cron_checker.exceptions import (
    IncrementOutOfBoundsError,
    PartCannotBeNoneError,
    PatternOrLiteralMatchError,
    RangeIncrementOutOfBoundsError,
    RangeOutOfBoundsError,
    SpecificsOutOfBoundsError,
    ValueOutOfBoundsError,
)
from quartz_cron_checker.parsers import (
    try_parse_increment,
    try_parse_int,
    try_parse_range,
    try_parse_range_with_increment,
    try_parse_specifics,
)
from quartz_cron_checker.validators import (
    validate_increment,
    validate_literals,
    validate_patterns,
    validate_range,
    validate_range_with_increment,
    validate_single_digit,
    validate_specifics,
)

from .constants import (
    DEFAULT_NUMERIC_PATTERNS,
    DOW_LIST,
    DOW_OCCURRENCE_PATTERN,
    DOW_RANGE_PATTERN,
    LAST_DAY_OF_MONTH,
    LAST_DOW_IN_MONTH_PATTERN,
    LAST_N_DAYS_OF_MONTH_PATTERN,
    LAST_WEEKDAY_OF_MONTH,
    LIST_OF_STRINGS_PATTERN,
    MONTH_LIST,
    MONTH_RANGE_PATTERN,
    NEAREST_WEEKDAY_DAY_OF_MONTH_PATTERN,
    SPECIFIC_DOW_PATTERN,
    SPECIFIC_MONTH_PATTERN,
)


@attrs.define
class CronFieldConfig:
    name: str
    min_value: int
    max_value: int
    increment_max: int
    allowed_literals: set[str] = attrs.field(factory=set)
    patterns: tuple[re.Pattern, ...] = attrs.field(factory=tuple)
    nullable: bool = False

    def validate(self, part: str) -> None:
        if part is None and not self.nullable:
            raise PartCannotBeNoneError(self.name)

        if (int_part := try_parse_int(part)) is not None:
            if not validate_single_digit(int_part, self.min_value, self.max_value):
                raise ValueOutOfBoundsError(
                    self.name, part, self.min_value, self.max_value
                )
            return

        if (inc := try_parse_increment(part, self.min_value)) is not None:
            if not validate_increment(
                *inc, self.min_value, self.max_value, self.increment_max
            ):
                raise IncrementOutOfBoundsError(self.name, part, self.increment_max)
            return

        if (r := try_parse_range(part)) is not None:
            if not validate_range(*r, self.min_value, self.max_value):
                raise RangeOutOfBoundsError(
                    self.name, part, *r, self.min_value, self.max_value
                )
            return

        if (ri := try_parse_range_with_increment(part)) is not None:
            if not validate_range_with_increment(*ri, self.min_value, self.max_value):
                raise RangeIncrementOutOfBoundsError(
                    self.name,
                    part,
                    *ri,
                    self.min_value,
                    self.max_value,
                    self.increment_max,
                )
            return

        if (spec := try_parse_specifics(part)) is not None:
            if not validate_specifics(
                spec, range(self.min_value, self.max_value + 1), self.allowed_literals
            ):
                raise SpecificsOutOfBoundsError(
                    self.name, part, spec, self.min_value, self.max_value
                )
            return

        if validate_literals(part, self.allowed_literals) or validate_patterns(
            part, self.patterns
        ):
            return

        raise PatternOrLiteralMatchError(
            self.name, part, self.patterns, self.allowed_literals
        )


SECOND_CONFIG = CronFieldConfig(
    name="second",
    min_value=0,
    max_value=59,
    increment_max=59,
    allowed_literals={"*"},
    patterns=DEFAULT_NUMERIC_PATTERNS,
)

MINUTE_CONFIG = attrs.evolve(SECOND_CONFIG, name="minute")

HOUR_CONFIG = attrs.evolve(
    SECOND_CONFIG,
    name="hour",
    min_value=0,
    max_value=23,
    increment_max=23,
)

YEAR_CONFIG = CronFieldConfig(
    name="year",
    min_value=1970,
    max_value=2099,
    increment_max=130,
    allowed_literals={"*"},
    patterns=DEFAULT_NUMERIC_PATTERNS,
    nullable=True,
)

DAY_OF_MONTH_CONFIG = CronFieldConfig(
    name="day_of_month",
    min_value=1,
    max_value=31,
    increment_max=31,
    allowed_literals={"*", "?", LAST_DAY_OF_MONTH, LAST_WEEKDAY_OF_MONTH},
    patterns=(
        *DEFAULT_NUMERIC_PATTERNS,
        LAST_N_DAYS_OF_MONTH_PATTERN,
        NEAREST_WEEKDAY_DAY_OF_MONTH_PATTERN,
    ),
)

MONTH_CONFIG = CronFieldConfig(
    name="month",
    min_value=1,
    max_value=12,
    increment_max=12,
    allowed_literals={*MONTH_LIST, "*"},
    patterns=(
        *DEFAULT_NUMERIC_PATTERNS,
        LIST_OF_STRINGS_PATTERN,
        MONTH_RANGE_PATTERN,
        SPECIFIC_MONTH_PATTERN,
    ),
)

DAY_OF_WEEK_CONFIG = CronFieldConfig(
    name="day_of_week",
    min_value=1,
    max_value=7,
    increment_max=7,
    allowed_literals={*DOW_LIST, "?", "*"},
    patterns=(
        *DEFAULT_NUMERIC_PATTERNS,
        DOW_OCCURRENCE_PATTERN,
        LAST_DOW_IN_MONTH_PATTERN,
        DOW_RANGE_PATTERN,
        SPECIFIC_DOW_PATTERN,
    ),
)
