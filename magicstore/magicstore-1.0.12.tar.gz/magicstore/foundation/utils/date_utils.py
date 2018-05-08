import datetime
from datetime import datetime as dt


def init_end_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def init_start_end():
    return (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")


def add_days(days, date):
    return dt.strftime(dt.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=days), "%Y-%m-%d")
