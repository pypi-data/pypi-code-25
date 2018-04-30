#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

(DIGIT, UNIT, SPACE) = tuple(range(3))
(STATE0, STATE1, STATE2, STATE3) = tuple(range(4))


def human2bytes(size, system='traditional', default_unit='M'):
    """Convert human readable size to the bytes
    `size`: the human readable size
    `default_unit`: the default unit when there is no unit after the `size`

    Using the `traditional` system, where a factor of 1024 is used::

    >>> human2bytes('35B')
    35
    >>> human2bytes('35 mB')
    36700160
    >>> human2bytes('35 GB')
    37580963840
    >>> human2bytes('35 TB')
    38482906972160
    >>> human2bytes('35 pb')
    39406496739491840
    >>> human2bytes('35 eb')
    40352252661239644160
    >>> human2bytes('35 zb')
    41320706725109395619840
    >>> human2bytes('  35 ')
    36700160

    Using the `SI` system, with a factor 1000
    >>> human2bytes('35B', system='si')
    35
    >>> human2bytes('35 mB', system='si')
    35000000
    >>> human2bytes('35 GB', system='si')
    35000000000
    >>> human2bytes('35 TB', system='si')
    35000000000000
    >>> human2bytes('35 pb', system='si')
    35000000000000000
    >>> human2bytes('35 eb', system='si')
    35000000000000000000
    >>> human2bytes('35 zb', system='si')
    35000000000000000000000
    >>> human2bytes('  35 ', system='si')
    35000000
    """
    unit_convert = {
        'traditional': {
            "B": 1,
            "K": 1024,
            "M": 1024 ** 2,
            "G": 1024 ** 3,
            "T": 1024 ** 4,
            "P": 1024 ** 5,
            "E": 1024 ** 6,
            "Z": 1024 ** 7,
        },
        'si': {
            "B": 1,
            "K": 1000,
            "M": 1000 ** 2,
            "G": 1000 ** 3,
            "T": 1000 ** 4,
            "P": 1000 ** 5,
            "E": 1000 ** 6,
            "Z": 1000 ** 7,
        },
    }

    size = size.upper()
    trans_table = [
        # digit, unit, space
        [1, -1, 0],  # State0
        [1, 3, 2],   # State1
        [-1, 3, 2],  # State2
        [-1, -1, 3],  # State3
    ]
    digit = ""

    state = STATE0
    it = enumerate(size)
    for i, c in it:
        if re.match(r"[0-9]", c):
            input_type = DIGIT
            digit += c
            state = trans_table[state][input_type]
        elif re.match(r"[BKMGTPEZ]", c):
            input_type = UNIT
            unit = c
            state = trans_table[state][input_type]
            if c == 'B':
                continue
            try:
                if size[i + 1] == 'B':
                    next(it)
            except IndexError:
                pass
            except:
                raise
        elif c == ' ':
            input_type = SPACE
            state = trans_table[state][input_type]
        else:
            state = -1

        if state == -1:
            break

    if state == 1 or state == 2:
        # 必须输入了UNIT才能够到达State3, 如果没到状态3，那么unit一定是默认的
        if 'unit' not in locals():
            unit = default_unit
        _bytes = int(digit) * unit_convert[system][unit]
    elif state == 3:
        _bytes = int(digit) * unit_convert[system][unit]
    elif state == -1:
        raise ValueError("size has wrong format: %s" % size)

    return _bytes


def bytes2human(size, system='alternative', precision=1):
    """Convert the bytes to the human readable size

    `size`: the bytes to convert

    Using the `traditional` system, where a factor of 1024 is used::

    >>> bytes2human(10)
    '10.00B'
    >>> bytes2human(100)
    '100.00B'
    >>> bytes2human(1000)
    '1000.00B'
    >>> bytes2human(10000)
    '9.77K'
    >>> bytes2human(20000)
    '19.53K'
    >>> bytes2human(100000)
    '97.66K'
    >>> bytes2human(200000)
    '195.31K'

    With a factor 1024, you also can use the `alternative`,
     `verbose`, `iec` to have different output format.
    >>> bytes2human(1000000, system='alternative')
    '976.56KB'
    >>> bytes2human(1000000, system='verbose')
    '976.56 kilobytes'
    >>> bytes2human(1000000, system='iec')
    '976.56Ki'

    Using the `si` system, with a factor 1000
    >>> bytes2human(10, system='si')
    '10.00B'
    >>> bytes2human(100, system='si')
    '100.00B'
    >>> bytes2human(1000, system='si')
    '1.00K'
    >>> bytes2human(10000, system='si')
    '10.00K'
    >>> bytes2human(20000, system='si')
    '20.00K'
    >>> bytes2human(100000, system='si')
    '100.00K'
    >>> bytes2human(200000, system='si')
    '200.00K'
    >>> bytes2human(1000000, system='si')
    '1.00M'
    """
    unit_convert = {
        'traditional': [
            (1024 ** 7, 'Z'),
            (1024 ** 6, 'E'),
            (1024 ** 5, 'P'),
            (1024 ** 4, 'T'),
            (1024 ** 3, 'G'),
            (1024 ** 2, 'M'),
            (1024 ** 1, 'K'),
            (1024 ** 0, 'B'),
        ],
        'alternative': [
            (1024 ** 7, 'ZB'),
            (1024 ** 6, 'EB'),
            (1024 ** 5, 'PB'),
            (1024 ** 4, 'TB'),
            (1024 ** 3, 'GB'),
            (1024 ** 2, 'MB'),
            (1024 ** 1, 'KB'),
            (1024 * 0, 'KB'),
            # (1024 ** 0, (' byte', ' bytes')),
        ],
        'verbose': [
            (1024 ** 7, (' zeetabyte', ' zeetabytes')),
            (1024 ** 6, (' petabyte', ' petabytes')),
            (1024 ** 5, (' ekabyte', ' ekabytes')),
            (1024 ** 4, (' terabyte', ' terabytes')),
            (1024 ** 3, (' gigabyte', ' gigabytes')),
            (1024 ** 2, (' megabyte', ' megabytes')),
            (1024 ** 1, (' kilobyte', ' kilobytes')),
            (1024 ** 0, (' byte', ' bytes')),
        ],
        'iec': [
            (1024 ** 7, 'Zi'),
            (1024 ** 6, 'Ei'),
            (1024 ** 5, 'Pi'),
            (1024 ** 4, 'Ti'),
            (1024 ** 3, 'Gi'),
            (1024 ** 2, 'Mi'),
            (1024 ** 1, 'Ki'),
            (1024 ** 0, ''),
        ],
        'si': [
            (1000 ** 7, 'Z'),
            (1000 ** 6, 'E'),
            (1000 ** 5, 'P'),
            (1000 ** 4, 'T'),
            (1000 ** 3, 'G'),
            (1000 ** 2, 'M'),
            (1000 ** 1, 'K'),
            (1000 ** 0, 'B'),
        ]
    }
    for factor, suffix in unit_convert[system]:
        if size >= factor:
            break
        elif size < 1024:
            amount = 0
            suffix = "KB"
            return ("%.{0}f".format(precision) % amount + suffix)

    amount = float(size / factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        suffix = singular if amount <= 1 else multiple
    # return "%.2f" % amount + suffix
    return ("%.{0}f".format(precision) % amount + suffix)
