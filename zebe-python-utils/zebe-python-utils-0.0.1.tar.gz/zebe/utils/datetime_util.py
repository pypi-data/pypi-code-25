# -*- coding: utf-8 -*-
import calendar


# 获取某一年总共有多少天
def get_total_day_of_year(year):
    total_day = 0
    for i in range(12):
        month_range = calendar.monthrange(year, i + 1)
        total_day += month_range[1]
    return total_day


# 获取某一天是当年的第几天
def get_which_day_of_year(year, month, day):
    target_day = dt.date(year, month, day)
    day_count = target_day - dt.date(target_day.year - 1, 12, 31)  # 减去上一年最后一天
    return day_count.days