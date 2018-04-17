from datetime import datetime, date

import pytest

from gpke_calendar.gpke_calendar import get_next_date
from .old_wimcal import dateList, minus9_plus9


@pytest.mark.parametrize("start , date, end", dateList)
def test_vs_wimcal_past(start, date, end):
    assert get_next_date(date, -9) == start

@pytest.mark.parametrize("start , date, end", dateList)
def test_vs_wimcal_future(start, date, end):
    assert get_next_date(date, +9) == end

def test_old_date():
    date = datetime.strptime('1970-01-01', '%Y-%m-%d')
    with pytest.raises(ValueError):
        get_next_date(date, 9)


def test_newer_than_2049_date():
    date = datetime.strptime('2050-01-01', '%Y-%m-%d')
    with pytest.raises(ValueError):
        get_next_date(date, 9)


def test_no_date():
    with pytest.raises(ValueError):
        get_next_date(None, 9)


def test_system_stand_still_day():
    assert date(2018, 1, 19) == get_next_date(date(2018, 2, 2), -9)
