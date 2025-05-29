# quartz-cron-checker

**quartz-cron-checker** is a lightweight, strict validator for [Quartz-style cron expressions](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html) in Python.

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

print(str(cron))  # "0 0 12 ? * MON-FRI"
```

You can also validate either a whole cron string or individual fields without creating an object:
```python
from quartz_cron_checker import validate_cron_string, validate_year, validate_second

# Validate a full cron string
validate_cron_string("0 0 12 ? * MON-FRI")  # Raises if invalid

# Validate individual fields
validate_second("0")  # Raises if invalid

validate_year("2023")  # Raises if invalid
```
