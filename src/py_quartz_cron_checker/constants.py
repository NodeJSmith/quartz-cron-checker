import calendar
import re

SINGLE_LITERAL_PATTERN = re.compile(r"^\d+$")
WILDCARD_PATTERN = re.compile(r"^\*$")
INCREMENT_PATTERN = re.compile(r"^(\*|\d+)(/\d+)$")
RANGE_PATTERN = re.compile(r"^\d+-\d+$")
RANGE_WITH_INCREMENT_PATTERN = re.compile(r"^\d+-\d+/\d+$")
LIST_OF_DIGITS_PATTERN = re.compile(r"^\d+(,\d+)+$")
LIST_OF_STRINGS_PATTERN = re.compile(r"^[A-Z]{3}(,[A-Z]{3})+$", re.IGNORECASE)


# DOW patterns
DOW_LIST = list(map(str.upper, calendar.day_abbr))
DOW_OR_PATTERN = f"({'|'.join(DOW_LIST)})"

DOW_OCCURRENCE_PATTERN = re.compile(r"\d+#\d+")
LAST_DOW_IN_MONTH_PATTERN = re.compile(r"\d+L", re.IGNORECASE)
DOW_RANGE_PATTERN = re.compile(f"^{DOW_OR_PATTERN}-{DOW_OR_PATTERN}$", re.IGNORECASE)
SPECIFIC_DOW_PATTERN = re.compile(
    f"^{DOW_OR_PATTERN}(,{DOW_OR_PATTERN})*$", re.IGNORECASE
)

# Month patterns
MONTH_LIST = list(map(str.upper, calendar.month_abbr))[1:]

MONTH_OR_PATTERN = f"({'|'.join(MONTH_LIST)})"
MONTH_RANGE_PATTERN = re.compile(
    f"^{MONTH_OR_PATTERN}-{MONTH_OR_PATTERN}$", re.IGNORECASE
)
SPECIFIC_MONTH_PATTERN = re.compile(
    f"^{MONTH_OR_PATTERN}(,{MONTH_OR_PATTERN})*$", re.IGNORECASE
)

# Day of month patterns
LAST_DAY_OF_MONTH = "L"
LAST_WEEKDAY_OF_MONTH = "LW"
LAST_N_DAYS_OF_MONTH_PATTERN = re.compile(r"^L-\d+$", re.IGNORECASE)
NEAREST_WEEKDAY_DAY_OF_MONTH_PATTERN = re.compile(r"^\d+W$", re.IGNORECASE)

DEFAULT_NUMERIC_PATTERNS = (
    RANGE_PATTERN,  # e.g. 1-31
    INCREMENT_PATTERN,  # e.g. 1/2
    RANGE_WITH_INCREMENT_PATTERN,  # e.g. 1-31/2
    LIST_OF_DIGITS_PATTERN,  # e.g. 1,2,3
)
