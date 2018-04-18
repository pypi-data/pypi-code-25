#!/usr/bin/env python3
# coding: utf-8
from __future__ import division, print_function

import re
from collections import defaultdict

from joker.cast import numerify

"""
textmanip: text manipulation functions
"""


def _deep_strip(s):
    s = s.replace('\r', '')
    s = s.replace('\n', '')
    return s.strip()


def _deep_strip_repr(x):
    return _deep_strip(repr(x))


def _regex_locate(regex, s):
    """
    :param regex: a returned value of re.compiled(pattern)
    :param s: a string 
    :return: an integer 
    """
    mat = regex.search(s)
    if mat is None:
        return -1
    return mat.pos


def _text_align(items, func_locate, func_format):
    rows = []
    maxpos = 0
    for item in items:
        pos = func_locate(item)
        line = func_format(item)
        rows.append((pos, line))
        maxpos = max(pos, maxpos)
    for pos, line in rows:
        if pos < 0:
            pos = maxpos
        yield ' ' * int(maxpos - pos) + line


def text_align_by_symbol(lines, symbol):
    lines = _text_align(
        lines,
        lambda s: s.find(symbol),
        _deep_strip,
    )
    return list(lines)


def text_align_by_pattern(lines, pattern):
    regex = re.compile(pattern)
    lines = _text_align(
        lines,
        lambda s: _regex_locate(regex, s),
        _deep_strip
    )
    return list(lines)


def text_align_for_dict(dic):
    """align colons"""
    dsr = _deep_strip_repr
    items = ((dsr(k), dsr(v)) for k, v in dic.items())
    lines = _text_align(
        items,
        lambda x: len(x[0]),
        lambda x: '{}: {}'.format(x[0], x[1]),
    )
    return list(lines)


def text_align_for_floats(numbers, precision=2):
    fmt = '{0:.{1}f}'
    lines = _text_align(
        numbers,
        lambda x: len(str(int(x))),
        lambda x: fmt.format(x, precision).rstrip('0'),
    )
    return list(lines)


def text_equal_width(lines, method='ljust'):
    lines = [str(x) for x in lines]
    maxlen = max(len(x) for x in lines)
    if method == 'center':
        return [x.center(maxlen) for x in lines]
    elif method == 'rjust':
        return [x.rjust(maxlen) for x in lines]
    else:
        return [x.ljust(maxlen) for x in lines]


def tabular_format(rows):
    rowcount = 0
    columns = defaultdict(list)
    columntypes = defaultdict(set)
    for row in rows:
        rowcount += 1
        for ic, cell in enumerate(row):
            cell = numerify(str(cell))
            columns[ic].append(cell)
            columntypes[ic].add(type(cell))

    types = [str, float, int]
    for ic in range(len(columns)):
        type_ = str
        for type_ in types:
            if type_ in columntypes[ic]:
                break
        if type_ == float:
            columns[ic] = text_align_for_floats(columns[ic])
        if type_ == int:
            just_method = 'rjust'
        else:
            just_method = 'ljust'
        columns[ic] = text_equal_width(columns[ic], method=just_method)
        print(ic, columns[ic])

    rows = []
    for ir in range(rowcount):
        row = []
        for ic in range(len(columns)):
            row.append(columns[ic][ir])
        rows.append(row)
    return rows


def find_common_prefix(lines):
    if not isinstance(lines, list):
        lines = list(lines)
    characters = []
    for column in zip(*lines):
        column = set(column)
        if len(column) > 1:
            break
        characters.append(list(column)[0])
    return ''.join(characters)


def find_common_suffix(lines):
    lines = [x[::-1] for x in lines]
    return find_common_prefix(lines)[::-1]
