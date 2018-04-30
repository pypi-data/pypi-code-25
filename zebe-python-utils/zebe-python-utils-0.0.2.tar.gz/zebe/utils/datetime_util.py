# -*- coding: utf-8 -*-
import calendar


# 获取某一年总共有多少天
import datetime


def get_total_day_of_year(year):
    total_day = 0
    for i in range(12):
        month_range = calendar.monthrange(year, i + 1)
        total_day += month_range[1]
    return total_day


# 获取某一天是当年的第几天
def get_which_day_of_year(year, month, day):
    target_day = datetime.date(year, month, day)
    day_count = target_day - datetime.date(target_day.year - 1, 12, 31)  # 减去上一年最后一天
    return day_count.days


# 获取某一天的开始时间
def get_start_of_day(which_day):
    return datetime.datetime.strptime(get_start_of_day_str(which_day), "%Y-%m-%d %H:%M:%S")


# 获取某一天的结束时间
def get_end_of_day(which_day):
    return datetime.datetime.strptime(get_end_of_day_str(which_day), "%Y-%m-%d %H:%M:%S")


# 获取某一天的开始时间（字符串）
def get_start_of_day_str(which_day):
    return which_day.strftime("%Y-%m-%d") + ' 00:00:00'


# 获取某一天的结束时间（字符串）
def get_end_of_day_str(which_day):
    return which_day.strftime("%Y-%m-%d") + ' 23:59:59'
