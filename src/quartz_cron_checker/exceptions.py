import re
from collections.abc import Sequence


class CronValidationError(ValueError):
    """Base class for all cron validation errors."""


class InvalidCronStructureError(CronValidationError):
    """Raised when the overall structure of a cron string is invalid.

    This includes cases like:
    - wrong number of parts
    - mutually exclusive fields both set to values
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidCronPartError(CronValidationError):
    part_name: str
    part_value: str | None

    def __init__(self, part_name: str, part_value: str | None, message: str) -> None:
        self.part_name = part_name
        self.part_value = part_value
        super().__init__(f"[{part_name}={part_value}] {message}")


class ValueOutOfBoundsError(InvalidCronPartError):
    def __init__(self, part_name: str, part_value: str, min_value: int, max_value: int) -> None:
        msg = f"Value {part_value} is out of bounds ({min_value}-{max_value})"
        super().__init__(part_name, part_value, msg)


class IncrementOutOfBoundsError(InvalidCronPartError):
    def __init__(self, part_name: str, part_value: str, increment_max: int) -> None:
        msg = f"Increment is out of bounds (1-{increment_max})"
        super().__init__(part_name, part_value, msg)


class RangeOutOfBoundsError(InvalidCronPartError):
    def __init__(
        self,
        part_name: str,
        part_value: str,
        start: int,
        end: int,
        min_value: int,
        max_value: int,
    ) -> None:
        msg = f"Range {start}-{end} is out of bounds ({min_value}-{max_value})"
        super().__init__(part_name, part_value, msg)


class RangeIncrementOutOfBoundsError(InvalidCronPartError):
    def __init__(
        self,
        part_name: str,
        part_value: str,
        start: int,
        end: int,
        increment: int,
        min_value: int,
        max_value: int,
        increment_max: int,
    ) -> None:
        msg = (
            f"Range with increment {start}-{end}/{increment} is out of bounds "
            f"({min_value}-{max_value}, 1-{increment_max})"
        )
        super().__init__(part_name, part_value, msg)


class SpecificsOutOfBoundsError(InvalidCronPartError):
    def __init__(
        self,
        part_name: str,
        part_value: str,
        values: Sequence[str],
        min_value: int,
        max_value: int,
    ) -> None:
        joined = ", ".join(values)
        msg = f"Specific values {joined} are out of bounds ({min_value}-{max_value})"
        super().__init__(part_name, part_value, msg)


class PatternOrLiteralMatchError(InvalidCronPartError):
    def __init__(
        self,
        part_name: str,
        part_value: str,
        patterns: Sequence[str],
        literals: set[str],
    ) -> None:
        pattern_str = ", ".join(p for p in patterns)
        literal_str = ", ".join(literals)
        msg = f"Part '{part_value}' does not match any literal ({literal_str}) or allowed pattern ({pattern_str})"
        super().__init__(part_name, part_value, msg)


class PatternSemanticValidationError(InvalidCronPartError):
    def __init__(
        self, part_name: str, part_value: str, pattern: re.Pattern, description: str, failure_hint: str | None = None
    ) -> None:
        msg = (
            f"Part '{part_value}' matches pattern {description!r} ('{pattern.pattern}') but failed semantic validation"
        )
        if failure_hint:
            msg += f": {failure_hint}"
        super().__init__(part_name, part_value, msg)


class PartCannotBeNoneError(InvalidCronPartError):
    def __init__(self, part_name: str) -> None:
        msg = "Part cannot be None"
        super().__init__(part_name, None, msg)
