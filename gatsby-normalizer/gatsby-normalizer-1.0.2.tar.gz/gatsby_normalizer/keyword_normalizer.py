"""
@author Gatsby Lee
@since 2018-05-22
"""

# ref: https://stackoverflow.com/questions/3411771/multiple-character-replace-with-python

SPECIAL_CHARS = ['~', '`', '!', '@', '%', '^', '*', '(', ')', '=', '{', '}', '|', '\\',
                 ';', '<', '>', ',', '?', ' +', '+ ', '\xe3\x80\x80', '\xe2\x80\xa8',
                 '"', '-', '+', ':', '#', '/', '[', ']']


def normalize_searchterm(keyword, spcial_chars=SPECIAL_CHARS,
                         func_list=[str.lower]):
    r"""
        Args:
            keyword (str)
            spcial_chars (list)
            func_list (list)
        Returns: kw (str)
    >>> normalize_searchterm('ABC ')
    'abc'
    >>> normalize_searchterm('A  B C')
    'a b c'
    >>> normalize_searchterm('A  B\tC')
    'a b c'
    >>> normalize_searchterm('A  B\nC')
    'a b c'
    >>> normalize_searchterm('     A  B  \nC   ')
    'a b c'
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

    >>> _replace_special_char('abc#', ['#', '!'])
    'abc'
    """

    for c in spcial_chars:
        if c in kw:
            kw = kw.replace(c, '')

    return kw


__all__ = ('normalize_searchterm',)
