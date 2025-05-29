import logging

from .checker import (
    QuartzCronChecker,
    validate_cron_string,
    validate_day_of_month,
    validate_day_of_month_or_week,
    validate_day_of_week,
    validate_hour,
    validate_minute,
    validate_month,
    validate_second,
    validate_year,
)


def enable_logging(level: int | str = logging.DEBUG) -> None:
    """Enable logging for the QuartzCronChecker module.

    Args:
        level (int): The logging level to set. Defaults to logging.DEBUG.
    """
    if not isinstance(level, int):
        if not hasattr(logging, level.upper()):
            raise ValueError(f"Invalid logging level: {level}")
        level = getattr(logging, level.upper())

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("quartz_cron_checker")
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False


__all__ = [
    "QuartzCronChecker",
    "enable_logging",
    "validate_cron_string",
    "validate_day_of_month",
    "validate_day_of_month_or_week",
    "validate_day_of_week",
    "validate_hour",
    "validate_minute",
    "validate_month",
    "validate_second",
    "validate_year",
]
