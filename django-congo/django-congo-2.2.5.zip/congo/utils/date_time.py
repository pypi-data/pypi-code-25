# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, time
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from random import randrange
from warnings import warn

def years_ago(years, from_date = None):
    if from_date is None:
        from_date = timezone.now()
    try:
        return from_date.replace(year = from_date.year - years)
    except:
        return from_date.replace(month = 2, day = 28, year = from_date.year - years)

# @og slabe rozwiazanie - do przebudowy
def get_default_start_date():
    warn(u"Use timezone.now() instead.", DeprecationWarning)
    return timezone.now().date()

# @og nie mozna podawac arg, do przebudowy!
def get_default_end_date(days_active):
    warn(u"Use in_14_days(), in_30_days(), in_60_days() or in_90_days() instead.", DeprecationWarning)
    return (timezone.now() + timedelta(days = days_active)).date()

def in_7_days():
    return timezone.now() + timedelta(days = 7)

def in_14_days():
    return timezone.now() + timedelta(days = 14)

def in_30_days():
    return timezone.now() + timedelta(days = 30)

def in_60_days():
    return timezone.now() + timedelta(days = 60)

def in_90_days():
    return timezone.now() + timedelta(days = 90)

def str_to_hour(value):
    warn(u"Use str_to_time() instead.", DeprecationWarning)
    return str_to_time(value)

def str_to_time(value, fmt = '%H:%M'):
    return datetime.strptime(value, fmt).time()

def hour_to_str(value):
    warn(u"Use time_to_str() instead.", DeprecationWarning)
    return time_to_str(value)

def time_to_str(value, fmt = '%H:%M'):
    return time.strftime(value, fmt)

def date_to_str(value, fmt = '%Y-%m-%d'):
    return datetime.strftime(value, fmt)

def datetime_to_str(value, fmt = '%Y-%m-%d %H:%M'):
    return datetime.strftime(value, fmt)

def str_to_date(date_str, fmt = '%Y-%m-%d'):
    return datetime.strptime(date_str, fmt)

def str_to_datetime(date_str, fmt = '%Y-%m-%d %H:%M'):
    return datetime.strptime(date_str, fmt)

def str_to_aware_datetime(date_str):
    result = parse_datetime(date_str)
    if not is_aware(result):
        result = make_aware(result)
    return result

def daterange(start_date, end_date):
    for delta in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days = delta + 1)

def check_timestamp(string, minutes = 3):
    try:
        timestamp = datetime.datetime.fromtimestamp(float(string))
        return abs(datetime.datetime.now() - timestamp) < datetime.timedelta(minutes = minutes)
    except ValueError:
        return False

def get_random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds = random_second)
