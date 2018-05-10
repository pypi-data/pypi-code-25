# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import importlib
import logging
import os
import time
import traceback
from pprint import pprint, pformat

from past.builtins import basestring

func_calls = {}
CONST_LINE = 40
TMP_BLACKLIST = [
    'odoo/odoo/service',
    '/odoo/odoo/http',
    '/lib/',
    '/site-packages/',
    'odoo/addons/web/',
    '/ir_http',
    'odoo/odoo/api',
]
TRACEBACK_BLACKLIST = [x.replace('/', '\\') for x in TMP_BLACKLIST]
TRACEBACK_BLACKLIST += [x.replace('/', '\\\\') for x in TMP_BLACKLIST]
TRACEBACK_BLACKLIST += TMP_BLACKLIST


def is_min(path):
    for traceback_bl in TRACEBACK_BLACKLIST:
        if traceback_bl in path:
            return False
    return True


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
        condition=True,
        logfile=False,
        use_pprint=True,
        log_context=False,
        log_user=False,
        log_names=False,
        log_fields_before=[],
        log_fields_after=[],
        log_fields_before_and_after=[],
        log_expr_before=[],
        log_expr_after=[],
        log_expr_before_and_after=[],
        api=False,
):
    def get_logger(name):
        if logger:
            return logger
        elif logfile and (not os.path.exists(logfile) or (os.path.isfile(logfile) and os.access(logfile, os.W_OK))):
            _logger = logging.getLogger(name)
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
            hdlr.setFormatter(formatter)
            _logger.addHandler(hdlr)
            _logger.setLevel(logging.DEBUG)
            return _logger
        return logger

    if logger and not logger_name:
        logger_name = logger.name
    elif logger and logger_name:
        logger = logging.getLogger(logger_name)
    logger = get_logger(logger_name or __name__)

    def logger_or_print(msg, func=False):
        if not isinstance(msg, unicode):
            msg = unicode(msg)
        if logger:
            logger.debug(pformat(msg))
        elif use_pprint:
            pprint(msg)
        else:
            print(msg)

    def real_decorator(func):
        def wrapper(*args, **kwargs):
            ctx = {}
            data = dict.fromkeys(filter(lambda arg: isinstance(arg, collections.Hashable), args), False)
            data.update(kwargs)
            for arg in args:
                if isinstance(arg, dict):
                    data.update(arg)
            if hasattr(args[0], 'ids') and hasattr(args[0], 'browse') and hasattr(args[0], 'env'):
                records = args[0]
                if len(records) > 0:
                    record = records[0]
                else:
                    record = False
                record_ids = records.ids
                record_user_id = records.env.user.id
                record_user_name = records.env.user.name
                record_user_login = records.env.user.login
                record_id = record.id if record else False
                record_names = records.mapped('display_name')
                records_context = records.env.context.copy() or data.get('context', {})
                ctx.update({
                    'self': records,
                    'env': records.env,
                    'object': record,
                    'objects': records,
                    'obj': record,
                    'model': records._name,
                    'model_name': records._name,
                    'records': records,
                    'record': record,
                    'active_ids': record_ids,
                    'ids': record_ids,
                    'active_id': record_id,
                    'id': record_id,
                    'names': record_names,
                    'context': records_context,
                    'record_user_id': record_user_id,
                    'record_user_name': record_user_name,
                    'record_user_login': record_user_login,
                    'data': data,
                })
            if isinstance(condition, basestring):
                condition_res = eval(condition, ctx)
            else:
                condition_res = bool(condition)
            if not condition_res:
                if api:
                    return api(func(*args, **kwargs))
                else:
                    return func(*args, **kwargs)
            stack = False
            if lines:
                logger_or_print("START ".ljust(CONST_LINE, '='))
            if ctx:
                if log_context:
                    logger_or_print('func=%s context=%s' % (func.__name__, ctx['context']))
                if log_user:
                    logger_or_print('func=%s uid=%s login=%s(%s)' % (
                        func.__name__, ctx['record_user_id'], ctx['record_user_login'], ctx['record_user_name']))
                if log_names:
                    logger_or_print('func=%s names=%s' % (func.__name__, ctx['names']))
            if log_min_traceback:
                stack = traceback.extract_stack()
                stack = filter(lambda item: is_min(item[0]), stack)
            if log_max_traceback:
                stack = traceback.extract_stack()
            if stack:
                for stack_item in stack:
                    stack_str = "File -> %s:%s [func=%s]" % (stack_item[0], stack_item[1], stack_item[2])
                    logger_or_print(stack_str)
                    stack_str = "   %s" % (stack_item[3],)
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
            if log_expr_before:
                logger_or_print(
                    'func=%s [before] expr<%s> : <%s>' % (func.__name__, log_expr_before, eval(log_expr_before, ctx)))
            if log_expr_before_and_after:
                logger_or_print('func=%s [before] expr<%s> : <%s>' % (
                    func.__name__, log_expr_before_and_after, eval(log_expr_before_and_after, ctx)))
            if log_fields_before or log_fields_before_and_after:
                for r in ctx.get('records', []):
                    tmp = "<%s>=<%s>"
                    tmp_line = []
                    for field in list(set(log_fields_before + log_fields_before_and_after)):
                        tmp_line.append(tmp % (field, getattr(r, field, '')))
                    logger_or_print(
                        'func=%s [%s] [before] id=%s %s' % (func.__name__, r._name, r.id, ' '.join(tmp_line)))
            start_time = time.time()
            if api:
                res = api(func(*args, **kwargs))
            else:
                res = func(*args, **kwargs)
            stop_time = time.time() - start_time
            if log_fields_after or log_fields_before_and_after:
                for r in ctx.get('records', []):
                    tmp = "<%s>=<%s>"
                    tmp_line = []
                    for field in list(set(log_fields_after + log_fields_before_and_after)):
                        tmp_line.append(tmp % (field, getattr(r, field, '')))
                    logger_or_print(
                        'func=%s [%s] [after] id=%s %s' % (func.__name__, r._name, r.id, ' '.join(tmp_line)))
            if log_expr_after:
                logger_or_print(
                    'func=%s [after] expr<%s> : <%s>' % (func.__name__, log_expr_after, eval(log_expr_after, ctx)))
            if log_expr_before_and_after:
                logger_or_print('func=%s [after] expr<%s> : <%s>' % (
                    func.__name__, log_expr_before_and_after, eval(log_expr_before_and_after, ctx)))
            if debug_after:
                importlib.import_module(debug_after).set_trace()
            if log_result:
                logger_or_print('func=%s result=%s' % (func.__name__, res))
            if log_types:
                logger_or_print('func=%s result type=%s' % (func.__name__, type(res)))
            if log_time:
                logger_or_print('func=%s execution took: %2.4f sec' % (func.__name__, stop_time))
            if lines:
                logger_or_print("END ".ljust(CONST_LINE, '='))
            return res

        return wrapper

    return real_decorator
