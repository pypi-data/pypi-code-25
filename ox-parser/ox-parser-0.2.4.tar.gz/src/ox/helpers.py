import re

from sidekick import fn
import sidekick


#
# Extract arguments from given positions.
#
@fn
def identity(x):
    """
    Return the argument unmodified.

    This is useful for composing with other functions.
    """
    return x


@fn
def constant(x):
    """
    Return a functiont that returns x no matter the argument.
    """
    return lambda *args: x


@fn
def singleton(x):
    """
    Return a list where x is the only element.
    """
    return [x]


@fn
def first(x, *args):
    """
    Return the first argument.
    """
    return x


@fn
def second(*args):
    """
    Return the second argument
    """
    return args[1]


@fn
def third(*args):
    """
    Return the third argument
    """
    return args[2]


@fn
def last(*args):
    """
    Return the last argument.
    """
    return args[-1]


@fn
def arg(i):
    """
    Return a function that selects only the last argument.
    """
    return lambda *args: args[i]


@fn
def args(*args):
    """
    Return the list of arguments.

    Example:
        >>> args(1, 2, 3)
        [1, 2, 3]
    """
    return list(args)


def pipeline(*funcs):
    """
    Create a pipeline of function application. It returns a new function that
    applies to the arguments in the same order as declared in the pipeline.

    >>> from math import sqrt
    >>> sqsum = pipeline(sqrt, sum)
    >>> sqsum([1, 4, 9])
    6.0
    """
    return fn(sidekick.compose(*funcs))


#
# Value treatment
#
OPEN_STRING = re.compile(r'''^[a-zA-Z]*['"]''')
CLOSE_STRING = re.compile(r'''['"]$''')
OPEN_TSTRING = re.compile(r'''^[a-zA-Z]*(''[']|""")''')
CLOSE_TSTRING = re.compile(r'''(''[']|""")$''')


@fn
def clean_string(data, open=OPEN_STRING, close=CLOSE_STRING):
    """
    Cleans quotes and escape sequences of a string literal.

    It accepts single quote and double quote strings with any arbitrary symbol
    prefix. Triple quoted strings are not accepted.
    """

    no_quotes = remove_quotes(open, close, data)
    return unescape_string(no_quotes)


@fn
def clean_triple_string(data, open=OPEN_TSTRING, close=CLOSE_TSTRING):
    """
    Like clean_string, but expect triple quoted strings.
    """
    return clean_string(data, open, close)


@fn.curried
def remove_quotes(open, close, data):
    """
    Remove quotes from data.

    Args:
        open, close:
            Regular expressions matching the start and end of string.
        data:
            String that needs to be cleaned.
    """
    # Remove opening quotes
    mo = open.match(data)
    if mo is None:
        raise ValueError('invalid string: %r' % data)
    clean = data[mo.end():]

    # Remove closing quotes
    matches = list(close.finditer(clean))
    if not matches:
        raise ValueError('invalid string: %r' % data)
    mo = matches[-1]
    clean = clean[:mo.start()]

    return clean


def unescape_string(data):
    r"""
    Unescape string escape sequences such as \n, \t, \uXXXX etc.
    """

    return data.encode('raw_unicode_escape').decode('unicode_escape')


#
# Higher order functions
#
def splice(func):
    """
    Takes a function that receives any number of args and transform it to a
    function that receives a single tuple argument.
    """

    @fn
    def func(args):
        return func(*args)

    return func


def flip(func):
    """
    Takes a function that receives two or more arguments and flip the first two
    before passing to the function.
    """

    @fn
    def flipped(x, y, *args):
        return func(y, x, *args)

    return flipped


def skip_and_call(f, *idx):
    """
    Return a function that skip all the given arguments (as denoted by position
    index) and calls f with the remaining ones.

    e.g.: ``skip_and_call(f, 0, 2)(a, b, c, d) ==> f(b, d)``.
    """
    idx = frozenset(idx)

    @fn
    def func(*args):
        new_args = tuple(x for i, x in enumerate(args) if i not in idx)
        return f(*new_args)

    return func


def select_and_call(f, *idx):
    """
    Return a function calls f using only the arguments selected by index.

    e.g.: ``select_and_call(f, 0, 1)(a, b, c, d) ==> f(a, b)``.
    """

    @fn
    def func(*args):
        return f(*(args[i] for i in idx))

    return func


def from_map(map):
    """
    Converts a map to a function.
    """

    @fn
    def func(x):
        try:
            return map[x]
        except KeyError:
            raise ValueError('invalid argument: %r' % x)

    return func


@fn
def cons(*args):
    """
    cons(x, *args, xs)  <==> [x] + xs.

    Return a cons join of the first and the last argument.

    This is useful in conjunction with "singleton" to handle rules associated
    with sequences as in the example::

        ox.make_parser([
            ('items : NUMBER', singleton),
            ('items : NUMBER COMMA items', cons),
        ])

    This function ignores the "COMMA" token (or any token besides the first and
    the last), and return ``[x] + xs`` where x is the first argument and
    items is the last one, which is assumed to be a list.
    """

    if len(args) <= 1:
        raise ValueError('requires at least 2 arguments')
    last = args[-1]
    if isinstance(last, list):
        return [args[0]] + last
    elif isinstance(last, tuple):
        return (args[0],) + last
    else:
        return type(last)([args[0]]) + last


@fn
def pair(*args):
    """
    pair(x, *args, y)  <==> [x, y].

    Similar to cons(), but does not expect the last argument to be a sequence.
    """
    if len(args) <= 1:
        raise ValueError('requires at least 2 arguments')
    return [args[0], args[-1]]
