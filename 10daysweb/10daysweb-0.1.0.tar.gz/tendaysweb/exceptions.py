# -*- coding: utf-8 -*-
from.utils import STATUS_CODES


class HttpException(Exception):
    def __init__(self, err_code: int, err: str=''):
        self.err_code = err_code
        self.err = err if err else STATUS_CODES.get(err_code, 'Unknown Error')
