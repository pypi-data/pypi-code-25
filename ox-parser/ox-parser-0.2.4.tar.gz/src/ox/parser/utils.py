import re
from types import MappingProxyType

#
# Token memo dictionaries map literal values to their natural token names.
# This mapping defines the default names for those literal values.
#
memo_names = dict(
    # Follow the approximate order of an american keyboard
    TILDE='~', BACKTICK='`', EXCLAMATION='!', AT='@', HASH='#', DOLLAR='$',
    PERCENT='%', HAT='^', AMP='&', ASTERISK='*', LPAREN='(', RPAREN=')',
    UNDERSCORE='_', MINUS='-', PLUS='+', EQUAL='=', LBRACE='{', RBRACE='}',
    PIPE='|', BACKSLASH='\\', COLON=':', SEMICOLON=';', DQUOTE='"', QUOTE="'",
    LT='<', GT='>', QUESTION='?', COMMA=',', DOT='.', DIV='/',

    # Escape sequences
    NEWLINE='\n', TAB='\t', CRETURN='\r',

    # Compound symbols
    LE='<=', GE='>=', EQ='==', NE='!=', NE2='<>', NE3='/=', ARROW='->',
    FATARROW='=>',
)
memo_dict = MappingProxyType({v: k + '_' for k, v in memo_names.items()})

#
# Utilities
#
IS_WORD_RE = re.compile(r'^[a-z_][a-z_0-9]*$')


def is_word(s):
    return bool(IS_WORD_RE.match(s))
