#!/usr/bin/env python

# encoding: utf-8

'''
 * Create File test_result_trey
 * Created by leixu on 2018/4/25
 * IDE PyCharm
'''

from RetryMe.retryme import result_retry, error_retry, SLEEPRULE
import arrow


@result_retry(expect_results=[None], retry_times=2, sleep_seconds=3)
def test_expect_results():
    print("expect_results")
    print(arrow.get())
    return None


@result_retry(unexpect_results=[None], retry_times=2, sleep_seconds=3)
def test_unexpect_results():
    print("unexpect_results")
    print(arrow.get())
    return None


@error_retry(retry_times=10, sleep_seconds=2, sleep_rule=SLEEPRULE.INCREASEPRO, sleep_rule_args={"max_sleep_time": 60})
@result_retry(unexpect_results=[None], retry_times=2, sleep_seconds=3)
def test_unexpect_results_and_retry():
    print("unexpect_results")
    print(arrow.get())
    return None


if __name__ == "__main__":
    test_unexpect_results_and_retry()
