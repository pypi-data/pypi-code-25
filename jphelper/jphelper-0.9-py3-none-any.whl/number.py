import jphelper.constant as consts
from math import floor, log


def to_japanese(number, use_kanji=False, decimal_limit=5, separator='', minus_sign=None):
    """Convert arabic numeral to hiragana (or kanji).

    :param float number: Real number.
    :param bool use_kanji: Use kanji instead of hiragana as output.
    :param int decimal_limit: Number of decimal places to be included in output.
    :param str separator: Separator character for each unit to aid reading (default empty character).
    :param str minus_sign: Custom minus sign (default katakana version).
    :return: Japanese reading of input number.
    :rtype: str
    """
    res = ''
    decimals_str = ''
    if isinstance(number, int):
        number = float(number)
    if number < 0:
        res = consts.minus if minus_sign is None else minus_sign
        number *= -1
    if number > consts.MAX_VAL:
        raise OverflowError('Maximum value ' + consts.MAX_VAL)

    idx = 1 if use_kanji else 0
    if not float.is_integer(number) and decimal_limit > 0:
        tmp = int((number - int(number))*10**decimal_limit)
        while tmp % 10 == 0:
            tmp = tmp // 10
        tmp = [int(x) for x in str(tmp)]
        for t in tmp:
            # decimals_str += consts.unit[t][idx]
            decimals_str = _join(separator, [decimals_str, consts.unit[t][idx]])
        decimals_str = _join(separator, [consts.period[idx], decimals_str])

    number = int(number)
    power = floor(log(number, 10)) if number != 0 else 0
    prevs = False
    while power >= 1:
        dv, number = divmod(number, 10**power)
        ten = power % 4
        if ten == 0:
            ten = power
        if dv > 0:
            if dv*(10**ten) in consts.specials.keys():
                # res += consts.specials[dv*(10**ten)][idx]
                res = _join(separator, [res, consts.specials[dv*(10**ten)][idx]])
            else:
                # res += consts.unit[dv][idx] + consts.tens[10**ten][idx]
                res = _join(separator, [res, consts.unit[dv][idx], consts.tens[ten][idx]])
            prevs = True
        elif prevs:
            if res != '' and power % 4 == 0:
                # res += consts.tens[10**ten][idx]
                res = _join(separator, [res, consts.tens[ten][idx]])
                prevs = False
        power -= 1
    if 0 <= number < 10 or res == '':
        # res += consts.unit[number][idx]
        res = _join(separator, [res, consts.unit[number][idx]])
    return _join(separator, [res, decimals_str])


def group_unit(number, separator=None, decimal_separator='.'):
    """Group number by ten thousandth.

    :param number: Real number to be groupped.
    :param separator: Group separator.
    :param decimal_separator: Decimal separator.
    :return: Number grouped every 4 digits except decimal parts.
    :rtype: str
    """
    res = ''
    minus = ''
    decimals = ''
    if separator is None:
        separator = consts.SEPARATOR
    if number < 0:
        minus = '-'
        number *= -1
    if isinstance(number, float):
        decimals = decimal_separator + str(number).split('.')[1]
        number = int(number)
    number = str(number)
    for i in range(len(number) - 1):
        res += number[i]
        if (len(number) - i - 1) % 4 == 0:
            res += separator
    res += number[-1]
    return minus + res + decimals


def kanji_grouping(number, use_minus_sign=True, use_hiragana=False, decimal_separator=None):
    """Add kanji/hiragana every multiple of ten thousands unit.

    :param float number: Real number.
    :param bool use_minus_sign: If True use '-' as minus sign, else use katakana version.
    :param bool use_hiragana: Use hiragana in place of kanji.
    :param str decimal_separator: Decimal separator.
    :return: Number with multipe of ten thousands unit character inserted.
    :rtype: str
    """
    idx = 0 if use_hiragana else 1
    minus, decimals = '', ''
    if number < 0:
        minus = '-' if use_minus_sign else consts.minus
        number *= -1
    if isinstance(number, float):
        decimals = consts.period[idx] + str(number).split('.')[1]
        number = int(number)
    number = str(number)
    res = ''
    start = 5 if len(number) > 4 and number[-1:-5:-1] == '0000' else 1
    for i in range(start, len(number) + 1):
        if i > 4 and (i - 1) % 4 == 0:
            res = consts.tens[i-1][idx] + res
        res = number[-i] + res
    return minus + res + decimals


def shorten(number, use_minus_sign=True, use_hiragana=False, decimal_places=1, decimal_separator=None):
    """Round number based on highest unit of 10e4.

    :param float number: Real number.
    :param bool use_minus_sign: If True use '-' as minus sign, else use katakana version.
    :param bool use_hiragana: Use hiragana in place of kanji.
    :param int decimal_places: Number of decimals included.
    :param str decimal_separator: Decimal separator.
    :return: Formatted number.
    :rtype: str
    """
    idx = 0 if use_hiragana else 1
    res, minus = '', ''
    if number < 0:
        minus = '-' if use_minus_sign else consts.minus
        number *= -1
    if decimal_separator is None:
        decimal_separator = consts.SEPARATOR
    number = str(int(number))
    if int(number) < 10000:
        res = number
    else:
        n_digit = len(number)
        taken = n_digit % 4
        unit = (n_digit // 4) * 4
        res = number[0:taken]
        if decimal_places > 0:
            decimals = number[taken:taken+decimal_places]
            if int(decimals) > 0:
                res = res + decimal_separator + decimals
        res += consts.tens[unit][idx]
    return minus + res


def _join(separator, lst):
    return separator.join([k for k in lst if k != ''])
