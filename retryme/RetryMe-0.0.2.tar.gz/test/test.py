#!/usr/bin/env python

# encoding: utf-8

'''
 * Create File test
 * Created by leixu on 2018/4/23
 * IDE PyCharm
'''
import asyncio
from RetryMe.retryme import error_retry, SLEEPRULE
import arrow


@error_retry(retry_times=2, sleep_seconds=3)
def test_normal_use_error():
    print(arrow.get())
    raise Exception("Error")


class BaseError(Exception):
    pass


class AnotherBaseError(Exception):
    pass


class TestError(BaseError):
    pass


@error_retry(exceptions=[BaseError], retry_times=2, sleep_seconds=3)
def test_spec_error():
    print(arrow.get())
    raise TestError("Error")


@error_retry(exceptions=[AnotherBaseError], retry_times=2, sleep_seconds=3)
def test_another_error():
    print(arrow.get())
    raise TestError("Error")


@error_retry(exceptions=[Exception], retry_times=2, sleep_seconds=3, )
def test_another_error():
    print(arrow.get())
    raise TestError("Error")


@error_retry(exceptions=[Exception], retry_times=10, sleep_seconds=2, sleep_rule=SLEEPRULE.INCREASE, sleep_rule_args={"step": 4})
def test_sleep_increase_rule_error():
    print(arrow.get())
    raise TestError("Error")


@error_retry(exceptions=[Exception], retry_times=10, sleep_seconds=2, sleep_rule=SLEEPRULE.INCREASEPRO, sleep_rule_args={"max_sleep_time": 60})
def test_sleep_increase_pro_rule_error():
    print(arrow.get())
    raise TestError("Error")


if __name__ == "__main__":
    test_sleep_increase_pro_rule_error()
    # test_normal_use_error()
    # test_test_error()
    # test_another_error()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_async_error())
    # loop.close()
