import calendar
import json
from itertools import chain, combinations, product
from pathlib import Path

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from py_quartz_cron_checker import CronStr

KNOWN_GOOD_VALUES = json.loads(
    Path(__file__).parent.joinpath("good_values.json").read_text()
)
BAD_VALUES = json.loads(Path(__file__).parent.joinpath("bad_values.json").read_text())


def powerset(iterable):
    s = list(iterable)
    # Start from 1 to exclude the empty set
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


@st.composite
def st_wildcard_value(draw):
    """Generate a wildcard value for day_of_month or day_of_week"""
    return draw(st.one_of(st.just("*"), st.just("?"), st.none()))


@st.composite
def st_month_of_year(draw):
    """Generate a month_of_year value"""
    # starting at [1:] because calendar.month_abbr[0] is an empty string (why??)
    str_months = list(calendar.month_abbr)[1:]
    num_months = list(range(1, 13))
    test_values = [str_months[0], str_months[3], str_months[6], str_months[9]]

    # <start>-<end> month of the year, e.g. Jan-Mar
    str_pairs = [f"{m1}-{m2}" for m1, m2 in combinations(str_months, 2)]

    # <start>-<end> month of the year, e.g. 1-3
    num_pairs = [f"{m1}-{m2}" for m1, m2 in combinations(num_months, 2)]

    # every Nth month of the year, starting on <month>, e.g. 4/1
    num_patterns = [f"{m1}/{m2}" for m1, m2 in combinations(num_months, 2)]

    # specific months of the year, e.g. Jan,Apr,Jul
    str_month_combos = [
        ",".join(sorted(group, key=test_values.index))
        for group in powerset(test_values)
    ]

    return draw(
        st.one_of(
            st.sampled_from(str_months),
            st.sampled_from(str_pairs),
            st.sampled_from(num_months),
            st.sampled_from(num_pairs),
            st.sampled_from(str_month_combos),
            st.sampled_from(num_patterns),
        )
    )


@st.composite
def st_day_of_week(draw):
    """Generate a day_of_week value"""
    str_days = list(calendar.day_abbr)
    num_days = list(range(1, 8))
    num_weeks_in_month = list(range(1, 6))

    test_values = [str_days[0], str_days[3], str_days[6]]

    # <start>-<end> day of the week, e.g. Mon-Fri
    str_pairs = [f"{d1}-{d2}" for d1, d2 in combinations(str_days, 2)]

    # <start>-<end> day of the week, e.g. 1-5
    num_pairs = [f"{d1}-{d2}" for d1, d2 in combinations(num_days, 2)]

    # every Nth day of the week, starting on <day>
    num_patterns = [f"{d1}/{d2}" for d1, d2 in combinations(num_days, 2)]

    # Nth occurrence of a weekday in a month, e.g. 5th Mon = 2#5
    num_occurrence = [f"{d1}#{d2}" for d1, d2 in product(num_days, num_weeks_in_month)]

    # specific days of the week, e.g. Mon,Wed,Fri
    str_day_combos = [
        ",".join(sorted(group, key=test_values.index))
        for group in powerset(test_values)
    ]

    # last day of the week in a month
    # e.g. last thursday = 5L
    last_day_of_week_in_month = [f"{d!s}L" for d in num_days]

    return draw(
        st.one_of(
            st.sampled_from(str_days),
            st.sampled_from(str_pairs),
            st.sampled_from(num_days),
            st.sampled_from(num_pairs),
            st.sampled_from(str_day_combos),
            st.sampled_from(num_patterns),
            st.sampled_from(num_occurrence),
            st.sampled_from(last_day_of_week_in_month),
        )
    )


@st.composite
def st_day_of_month(draw):
    """Generate a day_of_month value"""
    str_days = list(map(str, list(range(1, 32))))
    num_days = list(range(1, 32))
    test_values = [str_days[0], str_days[3], str_days[6]]

    # <start>-<end> day of the month, e.g. 1-31
    num_pairs = [f"{d1}-{d2}" for d1, d2 in combinations(num_days, 2)]

    # every Nth day of the month, starting on <day>, e.g. 1/2
    num_patterns = [f"{d1}/{d2}" for d1, d2 in combinations(num_days, 2)]

    # specific days of the month, e.g. 1,3,6
    str_day_combos = [
        ",".join(sorted(group, key=test_values.index))
        for group in powerset(test_values)
    ]

    # last N day(s) before the end of the month (tbh, not sure what this would do)
    last_n_days = [f"L-{d!s}" for d in num_days]

    # nearest weekday to the given day of the month
    nearest_weekday = [f"{d!s}W" for d in num_days]

    others = [
        "L",  # last day of the month
        "LW",  # last weekday of the month
    ]

    return draw(
        st.one_of(
            st.sampled_from(str_days),
            st.sampled_from(num_days),
            st.sampled_from(num_pairs),
            st.sampled_from(str_day_combos),
            st.sampled_from(num_patterns),
            st.sampled_from(others),
            st.sampled_from(last_n_days),
            st.sampled_from(nearest_weekday),
        )
    )


@st.composite
def st_simple_values(
    draw, min_value=0, max_value: int = 59, increment_max_value: int = 59
):
    """Generate a seconds or minutes value"""

    increment_range = list(range(1, increment_max_value + 1))

    values = list(range(min_value, max_value))
    test_values = list(map(str, [values[0], values[18], values[22]]))

    # every Nth second/minute/hour/year, starting on <value>, e.g. 0/2
    num_patterns = [f"{v1}/{v2}" for v1, v2 in product(values, increment_range)]

    # <start>-<end> second/minute/hour/year, e.g. 0-59
    num_pairs = [f"{v1}-{v2}" for v1, v2 in combinations(values, 2)]

    literals = ["*"]

    # specific seconds/minutes/hours/years, e.g. 0,20,30
    value_combos = [
        ",".join(sorted(group, key=test_values.index))
        for group in powerset(test_values)
    ]

    return draw(
        st.one_of(
            st.sampled_from(values),
            st.sampled_from(num_pairs),
            st.sampled_from(value_combos),
            st.sampled_from(num_patterns),
            st.sampled_from(literals),
        )
    )


@st.composite
def cron_string(draw):
    """Generate a cron string"""
    seconds = draw(st_simple_values(max_value=59))
    minutes = draw(st_simple_values(max_value=59))
    hours = draw(st_simple_values(max_value=23, increment_max_value=23))
    day_of_month = draw(st_day_of_month())
    month = draw(st_month_of_year())
    day_of_week = draw(st_day_of_week())
    year = draw(st_simple_values(2020, 2099, 129))

    wildcard_day_of_month = draw(st_wildcard_value())
    wildcard_day_of_week = draw(st_wildcard_value())

    assume(wildcard_day_of_month != wildcard_day_of_week)  # these two can't be the same
    assume(
        wildcard_day_of_month == "?" or wildcard_day_of_week == "?"
    )  # one of these must be a '?'

    true_day_of_week = wildcard_day_of_week or day_of_week
    true_day_of_month = wildcard_day_of_month or day_of_month

    # Create a cron string with the given values
    cron_str = f"{seconds} {minutes} {hours} {true_day_of_month} {month} {true_day_of_week} {year}"

    if cron_str not in KNOWN_GOOD_VALUES:
        print(f'"{cron_str}",')

    return cron_str


@given(cron_string())
@settings(deadline=None)
def test_valid_cron_string_returns_true(cron_str: str):
    """Tests that the cron string is valid"""

    assert CronStr.validate_cron_string(cron_str) is True

    parts = cron_str.split(" ")
    assert CronStr(*parts).validate() is True


@pytest.mark.parametrize("cron_str", list(BAD_VALUES.keys()))
def test_invalid_cron_string_returns_false(cron_str: str):
    """Tests that the cron string is invalid"""

    with pytest.raises(ValueError):
        reason = BAD_VALUES.get(cron_str, "Unknown reason")
        assert CronStr.validate_cron_string(cron_str) is False, reason

    parts = cron_str.split(" ")

    exc = ValueError if len(parts) >= 6 else TypeError

    with pytest.raises(exc):
        reason = BAD_VALUES.get(cron_str, "Unknown reason")
        assert CronStr(*parts).validate() is False, reason


@pytest.mark.parametrize("cron_str", KNOWN_GOOD_VALUES)
def test_known_good_cron_string(cron_str: str):
    """Tests that the cron string is known to be good"""

    assert CronStr.validate_cron_string(cron_str) is True, f"Failed for: {cron_str}"
    parts = cron_str.split(" ")
    assert CronStr(*parts).validate() is True, f"Failed for: {cron_str}"
