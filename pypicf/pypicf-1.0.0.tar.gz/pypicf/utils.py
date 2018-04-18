#!/usr/bin/env python
# coding: utf-8

import functools

from .logging import logger
from .exceptions import SearchError


def search_database(query, database):

    result = []

    for data in database:

        foundflag = False
        testcase = [
            data,
            data.title(),
            data.capitalize(),
            data.upper(),
            data.lower(),
        ]

        for case in testcase:

            if foundflag:
                continue

            if case.find(query) != -1:
                foundflag = True
                result.append(data)

    if len(result) == 0:
        raise SearchError("Classifiers not found.")

    return result


def prettyprint(classifiers, indent=4):

    margin = " " * indent

    context = "classifiers=[\n"
    for classifier in classifiers:
        context += margin + "\"{0}\",\n".format(classifier)
    context += "]"

    print context


def require_classifier(classifier_name):
    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            loop_flag = False
            while loop_flag is False:
                try:
                    return func(*args, **kwargs)
                    loop_flag = True

                except KeyboardInterrupt:
                    logger.require(classifier_name)
                    continue

                except Exception as e:
                    logger.error(type(e).__name__, e.message)
                    continue
        return wrapper
    return _decorator


def loop_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop_flag = False
        while loop_flag is False:
            try:
                return func(*args, **kwargs)
                loop_flag = True

            except Exception as e:
                logger.error(type(e).__name__, e.message)
                continue
    return wrapper
