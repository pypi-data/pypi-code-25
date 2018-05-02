# coding: utf-8 or # -*- coding: utf-8 -*-
import time
from datetime import datetime
import datetime as dt

class DateUtils:

    @staticmethod
    def to_int(datetime):
        return int(time.mktime(datetime.timetuple()))

    @staticmethod
    def to_datetime(datetime_int):
        return datetime.fromtimestamp(datetime_int)

    @staticmethod
    def to_datetime(datetime_str, format="%Y%m%d%H%M%S"):
        return datetime.strptime(datetime_str, format)

    @staticmethod
    def to_str(date_time, format="%Y%m%d%H%M%S"):
        return date_time.strftime(format)  # 转成字面整型字符串, e.g. date: 2009-12-08 16:34:00 -> '20091208163400'

    @staticmethod
    def now():
        return datetime.now()

    '''
    计算从start_date到end_date的所有日期数组（包含start_date, end_date）
    '''
    @staticmethod
    def calc_delta_days(start_date=None, end_date=None):
        timedelta = end_date - start_date
        return [start_date + dt.timedelta(days=int(i)) for i in range(0, timedelta.days+1)]


if __name__ == '__main__':
    start_date = DateUtils.to_datetime("20180302", "%Y%m%d")
    DateUtils.calc_delta_days(start_date, DateUtils.now())
    pass