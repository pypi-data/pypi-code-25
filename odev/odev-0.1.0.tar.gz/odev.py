# -*- coding: utf-8 -*-
import importlib
import logging
import time
from pprint import pprint, pformat
import traceback

func_calls = {}
CONST_LINE = 40


def debugit(
        log_args=False,
        log_result=False,
        log_time=False,
        logger_name=False,
        logger=False,
        log_types=False,
        log_ncalls=False,
        log_min_traceback=False,
        log_max_traceback=False,
        debug_before=False,
        debug_after=False,
        lines=False,
):
    """
    :param log_args:
    :param log_result:
    :param log_time:
    :param logger_name:
    :param logger:
    :param log_types:
    :param log_ncalls:
    :param log_min_traceback:
    :param log_max_traceback:
    :param debug_before:
    :param debug_after:
    :param lines:
    :return:

    EXAMPLE:
    odoo.models.BaseModel.create = debugit(
        log_time=True,
        log_types=True,
        log_args=True,
        log_result=True,
        logger_name='test_test',
        logger=logger,
        log_min_traceback=True,
        log_max_traceback=True,
        debug_before='pdb',
        debug_after='ipdb',
        lines=True,
    )(odoo.models.BaseModel.create)
    """

    def logger_or_print(msg):
        if isinstance(msg, unicode):
            msg = unicode(msg)
        if logger_name:
            logging.getLogger(logger_name).debug(pformat(msg))
        elif logger:
            logger.debug(pformat(msg))
        else:
            pprint(msg)

    def real_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            stack = False
            if lines:
                logger_or_print("START ".ljust(CONST_LINE, '='))
            if log_min_traceback:
                stack = traceback.extract_stack()
                stack = filter(lambda item: '/addons/' in item[0], stack)
            if log_max_traceback:
                stack = traceback.extract_stack()
            if stack:
                for stack_item in stack:
                    stack_str = "File -> %s:%s" % (stack_item[0], stack_item[1])
                    logger_or_print(stack_str)
                    stack_str = "    Func=<%s> Expr=%s" % (stack_item[2], stack_item[3])
                    logger_or_print(stack_str)
            if log_ncalls:
                arg_kwargs_str = "args=%s kwargs=%s" % (args, kwargs)
                func_calls.setdefault(func.__name__, {})
                func_calls[func.__name__].setdefault(arg_kwargs_str, 0)
                func_calls[func.__name__][arg_kwargs_str] += 1
                logger_or_print('func=%s same_args_ncalls=%s different_ncalls=%s total_ncalls=%s' % (
                    func.__name__,
                    func_calls[func.__name__][arg_kwargs_str],
                    len(func_calls[func.__name__].keys()),
                    sum(func_calls[func.__name__].values()),
                ))
            if log_args:
                logger_or_print('func=%s args=%s kwargs=%s' % (func.__name__, args, kwargs))
            if log_types:
                arg_types = [type(arg) for arg in args]
                kwarg_types = {k: type(v) for k, v in kwargs.items()}
                logger_or_print('func=%s types args=%s kwargs=%s' % (func.__name__, arg_types, kwarg_types))
            if debug_before:
                importlib.import_module(debug_before).set_trace()
            res = func(*args, **kwargs)
            if debug_after:
                importlib.import_module(debug_after).set_trace()
            if log_result:
                logger_or_print('func=%s result=%s' % (func.__name__, res))
            if log_types:
                logger_or_print('func=%s result type=%s' % (func.__name__, type(res)))
            if log_time:
                logger_or_print('func=%s execution took: %2.4f sec' % (func.__name__, time.time() - start_time))
            if lines:
                logger_or_print("END ".ljust(CONST_LINE, '='))
            return res

        return wrapper

    return real_decorator
