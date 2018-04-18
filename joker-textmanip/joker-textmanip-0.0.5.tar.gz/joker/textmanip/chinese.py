#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import re
from collections import deque

chsi_digits = '零一二三四五六七八九'

chtr_digits = '零壹贰叁肆伍陆柒捌玖'


def _repdiv(num, divisor):
    results = []
    while num:
        d, m = divmod(num, divisor)
        results.append(m)
        num = d
    return results


def i2ch_lt10k(num, digits, units):
    parts = deque()
    for u, n in enumerate(_repdiv(num, 10)):
        if n:
            parts.appendleft(units[u])
        parts.appendleft(digits[n])
    ch = ''.join(parts)
    ch = re.sub(r'零+$', '', ch, flags=re.UNICODE)
    ch = re.sub(r'零{2,}', '零', ch, flags=re.UNICODE)
    ch = re.sub(r'\s+', '', ch, flags=re.UNICODE)
    return ch


def i2chsi(num, digits, units):
    if num < 10:
        return digits[num]
    if num == 10:
        return units[1]
    if num < 20:
        return units[1] + digits[num % 10]
    parts = deque()
    for u8, n8 in enumerate(_repdiv(num, 10 ** 8)):
        if u8:
            parts.appendleft(units[5])
        for u4, n4 in enumerate(_repdiv(n8, 10 ** 4)):
            if u4:
                parts.appendleft(units[4])
            ch = i2ch_lt10k(n4, digits, units)
            parts.appendleft(ch)
    return ''.join(parts)


def integer_to_chsi(num):
    """Simplified characters used in mainland China"""
    return i2chsi(num, chsi_digits, ['', '十', '百', '千', '万', '亿'])


def integer_to_chsicap(num):
    """Tamper-safe characters used in mainland China"""
    return i2chsi(num, chtr_digits, ['', '拾', '佰', '仟', '万', '亿'])


def chinese_to_integer():
    pass
