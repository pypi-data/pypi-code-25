#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 3/16/18
"""
.. currentmodule:: luijo.logging
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Dear diary...
"""

import logging


# pylint: disable=too-few-public-methods
class Loggable(object):
    """
    This is a mixin for classes that require a logger.
    """
    @property
    def logger(self) -> logging.Logger:
        """
        Get the logger.

        :return: the logger
        """
        try:
            return getattr(self, '__logger__')
        except AttributeError:
            logger = logging.getLogger(
                '{module}.{cls}'.format(
                    module=self.__class__.__module__,
                    cls=self.__class__.__name__))
            self.__dict__['__logger__'] = logger
            return logger
