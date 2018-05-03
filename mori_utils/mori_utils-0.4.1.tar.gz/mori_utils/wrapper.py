# -*- coding: utf-8 -*-
#
# @Time    : 2018/4/24 上午11:14
# @Author  : Mori
# @Email   : moridisa@moridisa.cn
# @File    : __init__.py.py

import os
import time
import pickle
import logging
from typing import List
from . import CACHE_PATH, read_config
from .data_operator import __get_mysql_connection__, __get_mongo_connection__
from functools import wraps

logger = logging.getLogger('mori_utils')

__all__ = ['log', 'cache', 'mysql_inject', 'mongo_inject']


def mysql_inject(config_name: str = None, arg_name: str = 'mysql', commit: bool = False):
    def wrapper(func):
        @wraps(func)
        def __inner_wrapper__(*args, **kwargs):
            connection = __get_mysql_connection__(config_name)
            cursor = connection.cursor()
            kwargs.update({arg_name: cursor})
            data = func(*args, **kwargs)
            if commit:
                connection.commit()
            connection.close()
            return data

        return __inner_wrapper__

    return wrapper


def mongo_inject(config_name: str = None, arg_name: str = 'mongo', collection_name: str = None):
    config = read_config(config_name)

    def wrapper(func):
        @wraps(func)
        def __inner_wrapper__(*args, **kwargs):
            with __get_mongo_connection__(config_name) as mongo_client:
                db = mongo_client.get_database(config['db'])
                collection = db.get_collection(
                    collection_name if collection_name is not None else config['collection'])
                kwargs.update({arg_name: collection})
                data = func(*args, **kwargs)
            return data

        return __inner_wrapper__

    return wrapper


def log(func):
    """
    log on begging & ending

    :param func: callable
    :return: callable wrapper
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f'{func.__module__}.{func.__name__} Start')
        data = func(*args, **kwargs)
        logger.info(f'{func.__module__}.{func.__name__} Finish')
        return data

    return wrapper


def cache(expiretime: float = None,
          cache_by_args: List[int] = None,
          cache_by_kwargs: List[str] = None):
    """
    cache data to disk before return

    :param expiretime: cache file expire time, after expire func will run again to generate new data
    :return: callable wrapper
    """

    def wrapper(func):
        @wraps(func)
        def __inner_wraps__(*args, **kwargs):
            cache_file_name = os.path.join(CACHE_PATH, f'{func.__module__}.{func.__name__}')
            if cache_by_args and len(cache_by_args) != 0:
                cache_file_name = f'{cache_file_name}.cache_by_{[args[i] for i in cache_by_args]}'
            if cache_by_kwargs and len(cache_by_kwargs) != 0:
                cache_file_name = f'{cache_file_name}.cache_by_{[kwargs[i] for i in cache_by_kwargs]}'
            cache_file_name = f'{cache_file_name}.cache'

            if os.path.exists(cache_file_name):
                if expiretime is None:
                    data = pickle.load(open(cache_file_name, 'rb'))

                elif time.time() - os.path.getmtime(cache_file_name) < expiretime * 24 * 60 * 60:
                    data = pickle.load(open(cache_file_name, 'rb'))
                    logger.info(f'{func.__module__}.{func.__name__} load data from cache')
                else:
                    data = func(*args, **kwargs)
                    pickle.dump(data, open(cache_file_name, 'wb'))
            else:
                data = func(*args, **kwargs)
                pickle.dump(data, open(cache_file_name, 'wb'))
            return data

        return __inner_wraps__

    return wrapper
