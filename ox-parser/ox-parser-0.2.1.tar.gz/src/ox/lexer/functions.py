from collections import OrderedDict
from functools import wraps

from sidekick import fn
from .lexer import Lexer

# Helps mocking/patching during tests
_import = __import__
_input = input
_print = print


def make_lexer(rules, which='simple'):
    """
    A lexer factory.

    This function expects to receive a list of (tok_type, regex) strings and
    returns a function that tokenize an input string into a sequence of tokens.

    Args:
        rules:
            A list of rules.
        which ('auto', 'ply' or 'simple'):
            Lexer factory type.
    """

    if which == 'auto':
        which = 'simple'
    if which == 'ply':
        lexer = ply_lexer(rules)
    elif which == 'simple':
        lexer = simple_lexer(rules)
    else:
        raise ValueError('invalid lexer: %r' % which)

    @fn
    @wraps(lexer)
    def lex(expr, lazy=False):
        if lazy:
            return lexer(expr)
        else:
            return list(lexer(expr))

    return lex


def tokenize(rules, expr, which='auto'):
    """
    Tokenize expression using the given list of rules.

    If you want to run the lexer more than once, it is probably better to
    call the make_lexer() function prior passing the input expression.

    Args:
        rules:
            A list of rules (see :func:`make_lexer`)
        expr (str):
            The input string.
        which:
            Select the lexer strategy.
    """
    return make_lexer(rules, which=which)(expr)


def simple_lexer(rules):
    """
    A very simple lexer factory based on a recipe on Python's regex module.
    """

    cls = class_from_rules(rules)

    def lexer(source):
        lex = cls(source)
        return lex.itertokens()

    lexer.which = 'simple'
    return lexer


def ply_lexer(rules):
    """
    A lexer factory that uses PLY own lexer module to build tokens.

    It has the same interface as the simple_lexer() function.
    """

    cls = class_from_rules(rules)

    def lexer(source):
        lex = cls(source)
        return lex.itertokens_ply()

    lexer.which = 'ply'
    return lexer


def lexer_interact(lexer):
    """
    Keep asking a new expressions from lexer and prints the token stream.
    """

    while True:
        expr = _input('expr: ')
        if expr:
            _print(list(lexer(expr)))
        else:
            break


def class_from_rules(rules):
    namespace = OrderedDict(rules)
    return type('Lexer', (Lexer,), namespace)
