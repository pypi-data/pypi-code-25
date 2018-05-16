# -*- coding: utf-8 -*-

import sys


# Useful for very coarse version differentiation.
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = (str, )
else:
    string_types = (str, unicode)


def bytes_to_str(src, encoding='utf-8'):
    """
    字节流转化为字符串
    :param src:
    :param encoding:
    :return:
    """
    return src.decode(encoding=encoding) if isinstance(src, bytes) else src


def str_to_bytes(src, encoding='utf-8'):
    """
    字符串转字节流
    :param src:
    :param encoding:
    :return:
    """

    return src if isinstance(src, bytes) else src.encode(encoding=encoding)
