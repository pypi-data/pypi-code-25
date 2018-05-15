#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__title__ = 'pyfortified-dateutil'
__version__ = '0.1.1'
__version_info__ = tuple(__version__.split('.'))


import time
import pytz
import datetime as dt
import pytz_convert
import dateutil.rrule as dateutil_rrule
from dateutil.relativedelta import relativedelta

# def date_range_generator(start_date, end_date):
#     """Generate dates between start_date and end_date"""
#     assert start_date and end_date
#     for n in range(int ((end_date - start_date).days) + 1):
#         yield start_date + dt.timedelta(n)

def date_range_list(datetime_start, datetime_end, date_format='%04d-%02d-%02d'):
    assert datetime_start and datetime_end and date_format
    return [
        date_format % (d.year, d.month, d.day)
        for d in dateutil_rrule.rrule(dateutil_rrule.DAILY, dtstart=datetime_start, until=datetime_end)
    ]

def date_range_generator(datetime_start, datetime_end, date_format='%04d-%02d-%02d'):
    assert datetime_start and datetime_end and date_format
    return (
        date_format % (d.year, d.month, d.day)
        for d in dateutil_rrule.rrule(dateutil_rrule.DAILY, dtstart=datetime_start, until=datetime_end)
    )

def unixtime_to_datetime(unix_time_epoch_secs=None, tz_name='UTC'):
    """Unix time (also known as POSIX time[citation needed] or UNIX Epoch time)
    is a system for describing a point in time, defined as the number of seconds
    that have elapsed since 00:00:00 Coordinated Universal Time (UTC), Thursday, 1 January 1970.

    Args:
        unix_time_epoch_secs:
        tz_name:

    Returns:
        Datetime

    """
    if unix_time_epoch_secs is None:
        unix_time_epoch_secs = time.time()

    epoch_datetime = dt.datetime.fromtimestamp(unix_time_epoch_secs, pytz.timezone('UTC'))

    if tz_name is None or tz_name == 'UTC':
        return epoch_datetime

    return epoch_datetime.astimezone(pytz.timezone(tz_name))


def current_date():
    return dt.datetime.now().date().isoformat()

def dates_months_list(start_date, end_date, date_format="%Y-%m"):
    from dateutil.rrule import rrule, MONTHLY
    return [dt.strftime(date_format) for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]

def dates_months_generator(start_date, end_date, date_format="%Y-%m"):
    from dateutil.rrule import rrule, MONTHLY
    return (dt.strftime(date_format) for dt in rrule(MONTHLY, dtstart=start_date, until=end_date))

def dates_month_first_last(month_date, date_format="%Y-%m-%d"):
    if not (isinstance(month_date, str) or isinstance(month_date, dt.datetime) or isinstance(month_date, dt.date)):
        raise TypeError("Invalid date type: {0}".format(type(month_date)))

    _month_date = None
    if isinstance(month_date, str):
        _month_date = dt.datetime.strptime(month_date, date_format)
    elif isinstance(month_date, dt.datetime):
        _month_date = month_date.date()
    elif isinstance(month_date, dt.date):
        _month_date = month_date
    else:
        raise TypeError("Invalid date type: {0}".format(type(month_date)))

    month_last_date = _month_date + relativedelta(day=1, months=+1, days=-1)
    month_first_date = _month_date + relativedelta(day=1)
    return month_first_date, month_last_date