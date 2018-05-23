import jphelper.constant as const


def is_hiragana(text):
    """Check if all characters in text are hiragana."""
    res = True
    for t in text:
        if t not in const.HIRAGANA_SET:
            res = False
            break
    return res


def is_katakana(text):
    """Check if all characters in text are katakana."""
    res = True
    for t in text:
        if t not in const.KATAKANA_SET:
            res = False
            break
    return res


def is_kana(text):
    """Check if all characters in text are hiragana or katakana."""
    res = True
    for t in text:
        if t not in const.HIRAGANA_SET and t not in const.KATAKANA_SET:
            res = False
            break
    return res


def is_kanji(text, start_block=u'\u4e00', end_block=u'\u9fff'):
    """Check if all characters in text are kanji character. [CJK Unified Ideographs 4E00-9FFF Common]"""
    res = True
    for t in text:
        if t < start_block or t > end_block:
            res = False
            break
    return res


def match_reading(expression, reading, space=' ', post_space=''):
    """Match kanji in expression with its corresponding reading.

    :param str expression: Text contains mixture of kanji, hiragana, katakana, etc.
    :param str reading: Text equal to expression but using kana in place of kanji.
    :param str space: Character(s) to be inserted before kanji[furigana] group
    :param str post_space: Character(s) to be inserted after kanji[furigana] group
    :return: Text from expression with furigana attached after kanji.
    :rtype: str
    """
    # assert is_kana(reading)  # reading must be hiragana or katakana
    assert len(expression) > 0 and len(reading) > 0  # non empty string

    # if length of reading text less than expression (not possible), return expression
    if len(reading) < len(expression):
        reading = ''

    res, r_, k_, idx = '', '', '', len(expression) - 1
    _reading = reading[::-1]

    for r in _reading:
        if idx >= 0:
            if r == expression[idx]:
                if k_ == '' and r_ == '':
                    res = r + res
                else:
                    res = r + space + k_ + '[' + r_ + ']' + post_space + res
                    k_, r_ = '', ''
                idx -= 1
            else:
                if is_kanji(expression[idx]):  # if expression[idx] is KANJI_SET
                    k_ = expression[idx] + k_
                    idx -= 1
                    r_ = r + r_
                elif is_kana(expression[idx]):
                    r_ = r + r_
                else:
                    res = r + res
                    idx -= 1
        else:
            if r_ == '' and k_ == '':
                res = r + res
            else:
                r_ = r + r_
    if k_ != '':
        res = k_ + '[' + r_ + ']' + post_space + res
        r_ = ''
    if r_ != '':
        res = r_ + res
    return res if res != '' else expression  # return expression if no match or expression is kana


def kanaize(text, to_katakana=False):
    """Convert romaji to hiragana or katakana equivalent.

    :param str text: Romaji text.
    :param bool to_katakana: Result text will be in katakana if set True.
    :return: Kana version from input text.
    :rtype: str
    """
    k = 1 if to_katakana else 0
    # check long vowel
    ending = 'u' if not to_katakana else const.katakana_long_vowel
    if 'ō' in text:
        text = str.replace(text, 'ō', 'o' + ending)
    if 'ū' in text:
        text = str.replace(text, 'ū', 'u' + ending)
    if '-' in text and to_katakana:
        text = str.replace(text, '-', ending)
    # check double consonant
    for c in const.double_consonants:
        if c in text:
            text = str.replace(text, c, ('xtsu' + c[0]))
    # check small y
    for c in const.small_y:
        if c in text:
            text = str.replace(text, c, const.small_y[c])
    # change
    for c in const.small_kana:
        text = str.replace(text, c, const.small_kana[c][k])
    for c in const.kana2:
        text = str.replace(text, c, const.kana2[c][k])
    for c in const.kana:
        text = str.replace(text, c, const.kana[c][k])
    for c in const.vowel_kana:
        text = str.replace(text, c, const.vowel_kana[c][k])
    # replace n
    text = str.replace(text, 'nn', const.kana_n[k])
    text = str.replace(text, 'n', const.kana_n[k])
    # clean consonant
    check = 'kstnhmyrwgzjdbp'
    for c in check:
        text = str.replace(text, c, 'xtsu')
    # small kana
    for c in const.small_kana:
        text = str.replace(text, c, const.small_kana[c][k])
    return text
