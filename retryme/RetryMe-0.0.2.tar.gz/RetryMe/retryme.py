#!/usr/bin/env python

# encoding: utf-8

'''
 * Create File retryme
 * Created by leixu on 2018/4/23
 * IDE PyCharm
'''
import functools
from .logger import logger
import sys
import inspect
import time
import uuid
from enum import Enum

_result_check_flag = uuid.uuid4()
_if_version_bigger_than_35 = False

if sys.version_info > (3, 5, 0):
    _if_version_bigger_than_35 = True
    logger.info("Current version > 3.5,can use asyncio")


def try_raise(error):
    raise error


class BaseError(Exception):
    pass


class ArgError(BaseError):
    pass


class ResultStillUnexpectValueError(BaseError):
    pass


class ResultUnMatchedError(BaseError):
    pass


class SLEEPRULE(Enum):
    NORMAL = 1
    INCREASE = 2
    INCREASEPRO = 3

    @classmethod
    def _normal_gen(cls, sleep_seconds, retry_times):
        return [sleep_seconds for _ in range(retry_times + 1)]

    @classmethod
    def _increase_gen(cls, sleep_seconds, retry_times, step=1, **kwargs):
        def add():
            nonlocal sleep_seconds
            sleep_seconds = sleep_seconds + step
            return sleep_seconds

        return [sleep_seconds] + [add() for _ in range(retry_times)]

    @classmethod
    def _increase_pro_gen(cls, sleep_seconds, retry_times, max_sleep_time=None, **kwargs):
        def add():
            nonlocal sleep_seconds
            sleep_seconds = sleep_seconds * 2 + 3
            if max_sleep_time:
                return max_sleep_time if sleep_seconds > max_sleep_time else sleep_seconds
            else:
                return max_sleep_time

        return [add() for _ in range(retry_times)]


def _gen_sleep_time_list(sleep_rule, sleep_seconds, retry_times, sleep_rule_args):
    if sleep_rule:
        if isinstance(sleep_rule, SLEEPRULE):
            sleep_seconds_list = {
                SLEEPRULE.NORMAL: SLEEPRULE._normal_gen,
                SLEEPRULE.INCREASE: SLEEPRULE._increase_gen,
                SLEEPRULE.INCREASEPRO: SLEEPRULE._increase_pro_gen

            }[sleep_rule](sleep_seconds, retry_times, **sleep_rule_args)
    else:
        sleep_seconds_list = SLEEPRULE._normal_gen(sleep_seconds, retry_times)
    return sleep_seconds_list


def error_retry(exceptions=None, sleep_seconds=1, retry_times=1, sleep_rule=SLEEPRULE.NORMAL, sleep_rule_args={}):
    if exceptions and isinstance(exceptions, list):
        any_error_flag = False
    else:
        any_error_flag = True
    # the total run times   1 + retry_times
    total_times = retry_times + 1

    # gen sleep seconds list
    sleep_seconds_list = _gen_sleep_time_list(sleep_rule, sleep_seconds, retry_times, sleep_rule_args)

    def async_wrapper(func):
        import asyncio

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            result_flag = False
            _error = None
            result = _result_check_flag
            for i in range(total_times):
                retry_flag = False
                if result_flag:
                    break
                try:
                    result = await func(*args, **kwargs)
                    result_flag = True
                except Exception as e:
                    _error = e
                    if any_error_flag:
                        await asyncio.sleep(sleep_seconds_list[i])
                        continue
                    else:
                        for error in exceptions:
                            if isinstance(e, error):
                                await asyncio.sleep(sleep_seconds_list[i])
                                logger.debug("exception catch ,auto retry")
                                retry_flag = True
                                break
                    if retry_flag:
                        continue
                    raise e
            if result == _result_check_flag:
                raise _error
            else:
                return result

        return wrapped

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Some fancy foo stuff
            result_flag = False
            _error = None
            result = _result_check_flag
            for i in range(total_times):
                retry_flag = False
                if result_flag:
                    break
                try:
                    result = func(*args, **kwargs)
                    result_flag = True
                except Exception as e:
                    _error = e
                    if any_error_flag:
                        time.sleep(sleep_seconds_list[i])
                        continue
                    else:
                        for error in exceptions:
                            if isinstance(e, error):
                                time.sleep(sleep_seconds_list[i])
                                logger.debug("exception catch ,auto retry")
                                retry_flag = True
                                break
                    if retry_flag:
                        continue
                    raise e
            if result == _result_check_flag:
                raise _error
            else:
                return result

        return wrapped

    def switch_func(func):
        if inspect.iscoroutinefunction(func):
            return async_wrapper(func)
        else:
            return wrapper(func)

    return switch_func


def result_retry(expect_results=[], unexpect_results=[], sleep_seconds=1, retry_times=1, sleep_rule=SLEEPRULE.NORMAL, sleep_rule_args={}):
    expect_results_flag = False
    unexpect_results_flag = False
    expect_results_flag = True if expect_results and isinstance(expect_results, list) else False
    unexpect_results_flag = True if unexpect_results and isinstance(unexpect_results, list) else False

    1 if expect_results_flag or unexpect_results_flag else try_raise(ArgError("expect_results or unexpect_results should be set"))

    # the total run times   1 + retry_times
    total_times = retry_times + 1

    # gen sleep seconds list
    sleep_seconds_list = _gen_sleep_time_list(sleep_rule, sleep_seconds, retry_times, sleep_rule_args)

    def async_wrapper(func):
        import asyncio

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            result_flag = False
            result = _result_check_flag
            for i in range(total_times):
                if result_flag:
                    break
                try:
                    result = await func(*args, **kwargs)
                except Exception as e:
                    raise e
                if expect_results_flag and result in expect_results:
                    result_flag = True
                    break
                elif expect_results_flag:
                    await asyncio.sleep(sleep_seconds_list[i])
                    continue
                elif unexpect_results_flag and result in unexpect_results:
                    await asyncio.sleep(sleep_seconds_list[i])
                    continue
                elif unexpect_results_flag:
                    result_flag = True
                    break

            if result_flag:
                return result
            elif expect_results_flag:
                raise ResultUnMatchedError("still not get the matched expect result")
            elif unexpect_results_flag:
                raise ResultStillUnexpectValueError("the result is still in unexpect result list")

        return wrapped

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            result_flag = False
            result = _result_check_flag
            for i in range(total_times):
                if result_flag:
                    break
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    raise e
                if expect_results_flag and result in expect_results:
                    result_flag = True
                    break
                elif expect_results_flag:
                    time.sleep(sleep_seconds_list[i])
                    continue
                elif unexpect_results_flag and result in unexpect_results:
                    time.sleep(sleep_seconds_list[i])
                    continue
                elif unexpect_results_flag:
                    result_flag = True
                    break

            if result_flag:
                return result
            elif expect_results_flag:
                raise ResultUnMatchedError("still not get the matched expect result")
            elif unexpect_results_flag:
                raise ResultStillUnexpectValueError("the result is still in unexpect result list")

        return wrapped

    def switch_func(func):
        if inspect.iscoroutinefunction(func):
            return async_wrapper(func)
        else:
            return wrapper(func)

    return switch_func


def back_off():
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
