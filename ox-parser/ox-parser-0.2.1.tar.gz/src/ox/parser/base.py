from sidekick import fn
from .ebnf import ebnf_parser
from .ply import ply_parser


def make_parser(rules, start=None, *, debug=False, which='ebnf', **kwargs):
    r"""
    Return a parser from a list of (rule, handler) tuples:

    Args:
        rules (sequence):
            A list of (rule, handler). Each rule must be a single line string
            with a grammar rule. The handler function is called with the inputs
            declared on the grammar rule arguments. Usually each handler
            function returns a node in the parse tree.
        start (str):
            The start/root expression type. It will reduce the AST to the given
            start expression value. By default it uses the name of the first
            rule as the starting symbol
        debug (bool):
            If True, print debugging messages.
        which {'ply', 'ebnf'}:
            Select an specific grammar. The default value (ebnf) uses a extended
            BNF notation with conveniences such as repetitions, optional values,
            and more. See the documentation for more information on the allowed
            syntax for grammar rules.

    Usage:
        >>> import operator as op
        >>> import ox
        >>> from ox import helpers
        >>>
        >>> # A simple calculator lexer
        >>> lexer = ox.make_lexer([
        ...     ('NUMBER', r'\d+(\.\d*)?'),
        ...     ('SYMBOL', r'[-+*/()]'),
        ... ])
        >>>
        >>> # Now the parser (we pipe the result of the lexer to the parser)
        >>> parser = lexer >> ox.make_parser([
        ...     # Expression
        ...     ("expr : expr '+' term", op.add),
        ...     ("expr : expr '-' term", op.sub),
        ...     ("expr : term", helpers.identity),
        ...
        ...     # Terms
        ...     ("term : term '*' atom", op.mul),
        ...     ("term : term '/' atom", op.truediv),
        ...     ("term : atom", helpers.identity),
        ...
        ...     # Atoms
        ...     ("atom : NUMBER", float),
        ...     ("atom : '(' expr ')'", helpers.identity),
        ... ])
        >>>
        >>> # Let's try with a moderately complex expression
        >>> parser('2 + 10 * (1 + 2 + 3 + 4)')
        42
    """
    if which == 'ply':
        return fn(ply_parser(rules, start=start, debug=debug, **kwargs))
    elif which == 'ebnf':
        return fn(ebnf_parser(rules, start=start, debug=debug, **kwargs))
    else:
        raise ValueError('invalid parser type: %r' % which)
