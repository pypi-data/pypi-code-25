#!/usr/bin/env python

# encoding: utf-8

'''
 * Create File test_sleep_time_gen
 * Created by leixu on 2018/4/24
 * IDE PyCharm
'''
import asyncio
from RetryMe.retryme import error_retry, SLEEPRULE
import arrow


def test_normal_gen(sleep_seconds, retry_times):
    return SLEEPRULE._normal_gen(sleep_seconds, retry_times)


def test_increase_gen(sleep_seconds, retry_times, step):
    return SLEEPRULE._increase_gen(sleep_seconds, retry_times, step)


def test_increase_pro_gen(sleep_seconds, retry_times, max_sleep_time):
    return SLEEPRULE._increase_pro_gen(sleep_seconds, retry_times, max_sleep_time)


if __name__ == "__main__":
    print(test_normal_gen(2, 10))
    print(test_increase_gen(2, 10, 4))
    print(test_increase_pro_gen(2, 10, 60))
