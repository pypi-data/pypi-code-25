"""
@author Gatsby Lee
@since 2018-05-22
"""

# ref: https://stackoverflow.com/questions/3411771/multiple-character-replace-with-python

SPECIAL_CHARS = ['~', '`', '!', '@', '%', '^', '*', '(', ')', '=', '{', '}', '|', '\\',
                 ';', '<', '>', ',', '?', ' +', '+ ',
                 '"', '-', '+', ':', '#', '/', '[', ']']


def normalize_searchterm(keyword, spcial_chars=SPECIAL_CHARS,
                         func_list=[str.lower]):
    r"""
        Args:
            keyword (str)
            spcial_chars (list)
            func_list (list)
        Returns: kw (str)
    """

    kw = _replace_special_char(keyword, spcial_chars)
    # remove multiple space/tab/new line with one space
    kw = ' '.join(kw.split())
    for func in func_list:
        kw = func(kw)
    return kw


def _replace_special_char(kw, spcial_chars):
    """
    Replace special char specified in @spcial_chars to empty char
        Args: kw (str)
        Returns: kw (str)
    """

    for c in spcial_chars:
        if c in kw:
            kw = kw.replace(c, '')

    return kw


__all__ = (
    '_replace_special_char',
    'normalize_searchterm',)
