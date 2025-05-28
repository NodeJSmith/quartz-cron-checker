from .constants import (
    INCREMENT_PATTERN,
    LIST_OF_DIGITS_PATTERN,
    LIST_OF_STRINGS_PATTERN,
    RANGE_PATTERN,
    RANGE_WITH_INCREMENT_PATTERN,
    SINGLE_LITERAL_PATTERN,
)


def try_parse_int(value: str) -> int | None:
    """Try to parse a string as an integer, return None if it fails."""

    if value is None:
        return None

    if SINGLE_LITERAL_PATTERN.match(value) is None:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def try_parse_increment(part: str, min_value: int) -> tuple[int, int] | None:
    """Try to parse a cron increment expression of the form 'base/increment'.

    Args:
        part (str): The part to parse.

    Returns:
        tuple[int, int] | None: A tuple of (base, increment) if successful, None if it fails.
    """

    if INCREMENT_PATTERN.match(part) is None:
        return None

    base_str, increment_str = part.split("/", 1)

    try:
        base = min_value if base_str == "*" else int(base_str)
        increment = int(increment_str)
    except ValueError:
        return None

    return base, increment


def try_parse_range(part: str) -> tuple[int, int] | None:
    """Try to parse a range in the form 'start-end'."""
    if part is None:
        return None

    if RANGE_PATTERN.match(part) is None:
        return None

    pieces = part.split("-")
    if len(pieces) != 2:
        return None

    start = try_parse_int(pieces[0])
    end = try_parse_int(pieces[1])

    if start is None or end is None:
        return None

    return start, end


def try_parse_range_with_increment(part: str) -> tuple[int, int, int] | None:
    """Try to parse a 'start-end/increment' cron expression."""

    if part is None:
        return None

    if RANGE_WITH_INCREMENT_PATTERN.match(part) is None:
        return None

    range_part, increment_part = part.split("/", 1)
    range_vals = try_parse_range(range_part)
    if range_vals is None:
        return None

    if (increment := try_parse_int(increment_part)) is None:
        return None

    return (*range_vals, increment)


def try_parse_specifics(part: str) -> list[str] | None:
    """Try to parse a list of specific values, comma-separated."""
    if part is None:
        return None

    if LIST_OF_DIGITS_PATTERN.match(part) or LIST_OF_STRINGS_PATTERN.match(part):
        return [p.strip() for p in part.split(",")]

    return None
