from datetime import datetime

DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
WEB_DATETIME_FMT='%Y-%m-%dT%H:%M:%SZ'

def mw_str_to_date(date_str):
    return datetime.strptime(date_str,DATE_FMT)

def mw_str_to_datetime(time_str):
    return datetime.strptime(time_str,WEB_DATETIME_FMT)

def mw_time_to_timestamp(t):
    return int(t.timestamp())

def mw_date_to_str(date):
    return datetime.strftime(date, DATE_FMT)

def mw_datetime_to_str(t):
    return datetime.strftime(t,DATETIME_FMT)

def mw_timestamp_to_str(ts):
    t =datetime.fromtimestamp(ts)
    return mw_datetime_to_str(t)



