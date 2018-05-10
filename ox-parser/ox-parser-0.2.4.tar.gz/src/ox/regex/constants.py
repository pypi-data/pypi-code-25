from .functions import safe, repeat, optional
from .regex import Regex


#
# Helper functions (not part of the api)
#
def number_underscore(digit: Regex):
    return digit.repeat() + ('_' + digit.repeat()).repeat(0, ...)


#
# Special characters
#
digit = Regex(r'[0-9]')
non_digit = Regex(r'[^0-9]')
udigit = Regex(r'\d')
non_udigit = Regex(r'\D')

any_char = Regex(r'.')
ALL = Regex(r'(.|\s)')
string_start = Regex(r'^')
string_end = Regex(r'$')
ABSOLUTE_START = Regex(r'\A')
ABSOLUTE_END = Regex(r'\Z')
whitespace = Regex(r'\s')
non_whitespace = Regex(r'\S')
WORD = Regex(r'\w')
NON_WORD = Regex(r'\W')

# How do we describe those?
# BOUNDARY = Regex('\b')
# NO_BOUNDARY = Regex('\B')


#
# Common tokens
#

# Unsigned integers and natural numbers(0, 1, 42, 42, etc)
SIGN = \
    safe('+') | safe('-')

INT = \
    repeat(digit)

INT_UNDERSCORE = \
    number_underscore(digit)

# Rational numbers
DECIMAL_PART = \
    '.' + INT

FLOAT = \
    (INT + '.' + Regex(r'[0-9]*')) | DECIMAL_PART

FLOAT_UNDERSCORE = \
    (INT_UNDERSCORE + '.' + Regex(r'[0-9]*')) | DECIMAL_PART

# Generic number representations (both floats and ints)
NUMBER = \
    INT + optional(DECIMAL_PART) | DECIMAL_PART

NUMBER_UNDERSCORE = \
    INT_UNDERSCORE + optional(DECIMAL_PART) | DECIMAL_PART

# Integers in different bases. (Do not have the optional signed token)
BINARY_DIGIT = \
    Regex(r'[0-1]')

BINARY = \
    '0b' + repeat(BINARY_DIGIT)

BINARY_UNDERSCORE = \
    '0b' + number_underscore(BINARY_DIGIT)

OCTAL_DIGIT = \
    Regex(r'[0-7]')

OCTAL = \
    '0o' + repeat(OCTAL_DIGIT)

OCTAL_UNDERSCORE = \
    '0o' + number_underscore(OCTAL_DIGIT)

HEXADECIMAL_DIGIT = \
    Regex(r'[0-9a-fA-F]')

HEXADECIMAL = \
    r'0x' + repeat(HEXADECIMAL_DIGIT)

HEXADECIMAL_UNDERSCORE = \
    r'0x' + number_underscore(HEXADECIMAL_DIGIT)

# Strings and chars
CHAR = \
    Regex(r"'.'")

DQUOTE_STRING = \
    Regex(r'"[^"\\]*(\\.[^"\\]*)*"')

SQUOTE_STRING = \
    Regex(r"'[^'\\]*(\\.[^'\\]*)*'")

BQUOTE_STRING = \
    Regex(r"`[^`\\]*(\\.[^`\\]*)*`")

TRIPLE_DQUOTE_STRING = \
    Regex(r'""".*""""')

TRIPLE_SQUOTE_STRING = \
    Regex(r"'''.*'''")

TRIPLE_BQUOTE_STRING = \
    Regex(r"```.*```")

# Symbols
SYMBOL = \
    Regex(r'[a-zA-Z][a-zA-Z0-9_]*')

SYMBOL_DASH = \
    Regex(r'[a-zA-Z][a-zA-Z0-9-]*')

SYMBOL_BACKSLASH = \
    Regex(r'[a-zA-Z][a-zA-Z0-9/]*')

QUALIFIED_SYMBOL = \
    SYMBOL + ('.' + SYMBOL).repeat()

# Dates
_DD = Regex(r'[0-9]{2}')
_DDD = Regex(r'[0-9]{3}')
_DDDD = Regex(r'[0-9]{4}')
_DDDDDD = Regex(r'[0-9]{6}')

YEAR = _DDDD | SIGN + _DDDDDD
DATE = f'{YEAR}-{_DD}-{_DD}'
TIMEZONE = \
    'Z' | SIGN + _DD + optional(optional(':') + _DD)

TIME = \
    (f'{_DD}:{_DD}'
     + optional(f':{_DD}{optional(_DDD + optional(_DDD))}')
     + optional(TIMEZONE))

DATETIME = \
    Regex(r'{}(T{})?'.format(DATE, TIME))

# Comments
LINE = \
    Regex(r'[^\r\n]*')

PYTHON_COMMENT = \
    '#' + LINE

C_COMMENT = \
    '//' + LINE

C_BLOCK_COMMENT = \
    Regex(r'/\*(:?[^*]*[*][^/])+\*/')

LISP_COMMENT = \
    ';' + LINE

HASKELL_COMMENT = \
    '--' + LINE

HASKELL_BLOCK_COMMENT = \
    Regex(r'\{\-(?:[^-]*\-[^}])+\-\}')


# Print the import statement that imports names of constants in the module.
#
# (this is not an elegant solution, but we do not want to inject those
# name directly on globals or to use an wildcard import in order to make
# static analysis tools happier)
def _print_constants_import():
    data = ', '.join(k for k in globals() if k.isupper())
    print('from .constants import (%s)' % data)
