from dataclasses import dataclass, field, replace
from logging import getLogger
from typing import Literal

from quartz_cron_checker.exceptions import (
    IncrementOutOfBoundsError,
    PartCannotBeNoneError,
    PatternOrLiteralMatchError,
    PatternSemanticValidationError,
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
    LAST_N_DAYS_OF_MONTH_VALIDATOR,
    NEAREST_WEEKDAY_VALIDATOR,
    PatternValidator,
    validate_increment,
    validate_literals,
    validate_range,
    validate_range_with_increment,
    validate_single_digit,
    validate_specifics,
)

from .constants import DOW_LIST, LAST_DAY_OF_MONTH, LAST_WEEKDAY_OF_MONTH, MONTH_LIST
from .validators import (
    DEFAULT_NUMERIC_VALIDATORS,
    DOW_OCCURRENCE_VALIDATOR,
    DOW_RANGE_VALIDATOR,
    LAST_DOW_IN_MONTH_VALIDATOR,
    LIST_OF_STRINGS_VALIDATOR,
    MONTH_RANGE_VALIDATOR,
    SPECIFIC_DOW_VALIDATOR,
    SPECIFIC_MONTH_VALIDATOR,
)

LOGGER = getLogger(__name__)


@dataclass
class CronFieldConfig:
    name: str
    min_value: int
    max_value: int
    increment_max: int
    allowed_literals: set[str] = field(default_factory=set)
    pattern_validators: tuple[PatternValidator, ...] = field(default_factory=tuple)
    nullable: bool = False

    @property
    def _pattern_descriptions(self) -> list[str]:
        """Get a list of descriptions for the patterns."""
        return [validator.description for validator in self.pattern_validators]

    def validate(self, part: str) -> Literal[True]:
        """Validate a cron field part against the configuration.

        Args:
            part (str): The cron field part to validate.

        Raises:
            PartCannotBeNoneError: If the part is None and the field is not nullable.
            ValueOutOfBoundsError: If the part is an integer out of bounds.
            IncrementOutOfBoundsError: If the part is an increment out of bounds.
            RangeOutOfBoundsError: If the part is a range out of bounds.
            RangeIncrementOutOfBoundsError: If the part is a range with increment out of bounds.
            SpecificsOutOfBoundsError: If the part contains specific values out of bounds.
            PatternOrLiteralMatchError: If the part does not match any allowed patterns or literals.

        Returns:
            Literal[True]: Returns True if the part is valid.
        """
        if part is None and not self.nullable:
            raise PartCannotBeNoneError(self.name)

        # Remove internal whitespace - cron field values never allow it
        part = str(part).replace(" ", "")

        # validate literals - the function will also handle uppercase/lowercase/etc.
        if validate_literals(part, self.allowed_literals):
            LOGGER.debug("Part %r with value %r is in allowed literals", self.name, part)
            return True

        # simplest of all cases - a single digit, e.g. 1, 2, 3
        if (int_part := try_parse_int(part)) is not None:
            if not validate_single_digit(int_part, self.min_value, self.max_value):
                raise ValueOutOfBoundsError(self.name, part, self.min_value, self.max_value)
            LOGGER.debug("Part %r with value %r is a valid single digit", self.name, part)
            return True

        # handle increments, e.g. 1/2, 3/4
        if (inc := try_parse_increment(part, self.min_value)) is not None:
            if not validate_increment(*inc, self.min_value, self.max_value, self.increment_max):
                raise IncrementOutOfBoundsError(self.name, part, self.increment_max)
            LOGGER.debug("Part %r with value %r is a valid increment", self.name, part)
            return True

        # simple range, e.g. 1-31
        if (r := try_parse_range(part)) is not None:
            if not validate_range(*r, self.min_value, self.max_value):
                raise RangeOutOfBoundsError(self.name, part, *r, self.min_value, self.max_value)
            LOGGER.debug("Part %r with value %r is a valid range", self.name, part)
            return True

        # didn't know you could even do this, but it is valid in Quartz
        # e.g. 1-31/2 (every 2 days between the 1st and 31st)
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
            LOGGER.debug("Part %r with value %r is a valid range with increment", self.name, part)
            return True

        # specifics, such as Mon, Wed or 1,2,3
        if (spec := try_parse_specifics(part)) is not None:
            if not validate_specifics(spec, range(self.min_value, self.max_value + 1), self.allowed_literals):
                raise SpecificsOutOfBoundsError(self.name, part, spec, self.min_value, self.max_value)
            LOGGER.debug("Part %r with value %r is in allowed specifics", self.name, part)
            return True

        # these are pattern validators - they pair a pattern with a validator function
        # and also include a description and, possibly, a failure hint
        if self.pattern_validators:
            for validator in self.pattern_validators:
                pattern_matched, validation_passed = validator.validate(part)
                if not pattern_matched:
                    continue
                if pattern_matched and validation_passed:
                    return True
                if pattern_matched and not validation_passed:
                    LOGGER.debug("Part %r with value %r failed a pattern validator", self.name, part)
                    raise PatternSemanticValidationError(
                        self.name, part, validator.pattern, validator.description, validator.failure_hint
                    )

        raise PatternOrLiteralMatchError(self.name, part, self._pattern_descriptions, self.allowed_literals)


SECOND_CONFIG = CronFieldConfig(
    name="second",
    min_value=0,
    max_value=59,
    increment_max=59,
    allowed_literals={"*"},
    pattern_validators=DEFAULT_NUMERIC_VALIDATORS,
)

MINUTE_CONFIG = replace(SECOND_CONFIG, name="minute")

HOUR_CONFIG = replace(
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
    pattern_validators=DEFAULT_NUMERIC_VALIDATORS,
    nullable=True,
)

DAY_OF_MONTH_CONFIG = CronFieldConfig(
    name="day_of_month",
    min_value=1,
    max_value=31,
    increment_max=31,
    allowed_literals={"*", "?", LAST_DAY_OF_MONTH, LAST_WEEKDAY_OF_MONTH},
    pattern_validators=(*DEFAULT_NUMERIC_VALIDATORS, LAST_N_DAYS_OF_MONTH_VALIDATOR, NEAREST_WEEKDAY_VALIDATOR),
)

MONTH_CONFIG = CronFieldConfig(
    name="month",
    min_value=1,
    max_value=12,
    increment_max=12,
    allowed_literals={*MONTH_LIST, "*"},
    pattern_validators=(
        *DEFAULT_NUMERIC_VALIDATORS,
        LIST_OF_STRINGS_VALIDATOR,
        MONTH_RANGE_VALIDATOR,
        SPECIFIC_MONTH_VALIDATOR,
    ),
)

DAY_OF_WEEK_CONFIG = CronFieldConfig(
    name="day_of_week",
    min_value=1,
    max_value=7,
    increment_max=7,
    allowed_literals={*DOW_LIST, "?", "*"},
    pattern_validators=(
        *DEFAULT_NUMERIC_VALIDATORS,
        DOW_OCCURRENCE_VALIDATOR,
        LAST_DOW_IN_MONTH_VALIDATOR,
        DOW_RANGE_VALIDATOR,
        SPECIFIC_DOW_VALIDATOR,
    ),
)
