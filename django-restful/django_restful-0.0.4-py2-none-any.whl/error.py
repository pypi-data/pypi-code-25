# -*- coding: utf-8 -*-


class RestfulApiError(Exception):
    """Base class for RestfulApi errors"""

    @property
    def message(self):
        '''Returns the first argument used to construct this error.'''
        return self.args[0]


class DoesNotExistError(RestfulApiError):
    """数据不存在错误"""
    pass
