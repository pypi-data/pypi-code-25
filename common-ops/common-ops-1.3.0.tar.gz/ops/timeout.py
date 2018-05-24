#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 08/02/2018 13:26
# @Author  : Liozza
# @Site    : 
# @File    : timeout
# @Software: PyCharm
import signal
import functools
import sys


class TimeoutException(Exception):
    pass


def timeout(seconds, error_message="Timeout Exception!"):
    def decorated(func):
        result = ""

        def _handle_timeout(signum, frame):
            global result
            result = error_message
            raise TimeoutException(error_message)

        def wrapper(*args, **kwargs):
            global result
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
                return result
            except TimeoutException, e:
                print "%s after running %ss " % (e, seconds)
                sys.exit()
            finally:
                signal.alarm(0)

        return functools.wraps(func)(wrapper)

    return decorated
