# quartz-cron-checker

**quartz-cron-checker** is a lightweight (zero dependencies!), strict validator for [Quartz-style cron expressions](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html) in Python.

It ensures all parts of the cron string conform to the Quartz cron spec—including support for special characters, named values, and mutual exclusivity of day-of-month and day-of-week.

## Features

- ✅ Full support for 6- or 7-field Quartz cron expressions (`second minute hour day-of-month month day-of-week [year]`)
- ✅ Literal handling (`*`, `?`, `L`, `W`, `#`)
- ✅ Named months (`JAN`, `FEB`, etc.) and days (`MON`, `TUE`, etc.)
- ✅ Detailed error messages and exceptions
- ✅ Clean object-oriented API
- ✅ Extensible field-level validation

## Installation

```bash
pip install quartz-cron-checker
```

## Usage

Calling `validate` will raise an exception if the cron string is invalid. The method will return `True` otherwise.

```python
from quartz_cron_checker import QuartzCronChecker

# Parse and validate a cron string
cron = QuartzCronChecker.from_cron_string("0 0 12 ? * MON-FRI")
cron.validate()  # Raises if invalid

# __str__ returns the original cron string
print(cron)
>>> 0 0 12 ? * MON-FRI

# __repr__ returns a more detailed representation
print(repr(cron))
>>> <QuartzCronChecker(second=0, minute=0, hour=12, day_of_month=?, month=*, day_of_week=MON-FRI, year=None)>
```

You can also validate either a whole cron string or individual fields without creating an object:
```python
from quartz_cron_checker import validate_cron_string, validate_day_of_month, validate_second

# Validate a full cron string
print(validate_cron_string("0 0 12 ? * MON-FRI"))
>>> True

print(validate_cron_string("0 0 12 ? * MON-FRI-SAT"))
>>> PatternOrLiteralMatchError: [day_of_week=MON-FRI-SAT] Part 'MON-FRI-SAT' does not match any literal (THU, FRI, MON, SAT, TUE, WED, *, SUN, ?) or allowed pattern (Range, Increment, Range with increment, List of digits, Day of week occurrence, Last day of week in month, Day of week range, Specific day of week)


# Validate individual fields
print(validate_second("0"))
>>> True

print(validate_day_of_month("13/26"))
>>> True

print(validate_day_of_month("31W"))
>>> True

print(validate_day_of_month("33W"))
>>> PatternValidatorError: [day_of_month=33W] Part '33W' matches pattern 'Nearest weekday' ('^(\d+)W$') but failed semantic validation: must be between 1 and 31
```
