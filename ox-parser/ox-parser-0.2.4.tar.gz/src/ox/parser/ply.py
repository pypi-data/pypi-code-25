import os
import re
import sys
from collections import Counter

import typing
from ply import yacc

from sidekick import record

FINAL_TOKEN_NAME = re.compile(r'[_A-Z][A-Z0-9_]*')


def ply_parser(rules, start=None, debug=True, outdir=None, tokens=None):
    """
    PLY implementation of the LR parser.
    """

    # Validate
    if start is not None and not isinstance(start, str):
        msg = '"start" must be a string with the name of the starting rule'
        raise TypeError(msg)

    # Pre-processing
    tokens = tokens if tokens is not None else get_token_list(rules)
    rules = list(simplify_rules(rules))

    # We use a similar strategy as in the ply_lexer function, but this time
    # the process is more involving. Let us start with a very basic namespace
    # that does not define any p_<rule>_<id> functions yet.
    namespace = dict(
        tokens=tokens,
        p_error=lambda p: ply_parser_error(p, ply_parser, debug),
    )

    # Now we create rules from the input list
    counter = Counter()
    for rule, handler in rules:
        name = rule.partition(':')[0].strip()
        if start is None:
            start = name

        rule_id = counter[name] = counter[name] + 1
        rule_name = 'p_%s_%s' % (name, rule_id)
        namespace[rule_name] = make_rule_handler(rule, handler)

    # Add the p_empty rule on demand
    if requires_empty_rule(rules):
        namespace['p_empty'] = p_empty = lambda p: None
        p_empty.__doc__ = 'empty :'

    # We build a module-like object from namespace dictionary
    module = record(**namespace)
    outdir = outdir or get_caller_file()

    parser = parser_function_factory(module, start, debug, outdir)
    ply_parser = parser.ply_parser  # used on error messages
    return parser


def parser_function_factory(module, start, debug, outdir):
    """
    Create yacc module and the corresponding parsing function.
    """
    ply_parser = yacc.yacc(module=module, start=start, debug=debug,
                           outputdir=outdir, errorlog=Logger(sys.stderr))

    def parser(tokens: typing.Iterable):
        """
        Parse sequence of tokens.
        """

        if isinstance(tokens, str):
            raise ValueError('parser receives a list of tokens, not a string!')
        tk_list = list(tokens)
        tk_list.reverse()

        def next_token():
            if tk_list:
                return tk_list.pop()

        return ply_parser.parse(lexer=record(token=next_token))

    parser.ply_parser = ply_parser
    return parser


def ply_parser_error(p, parser=None, debug=False):
    """
    Function that is executed when PLY encounters a syntax error.
    """

    if p is None:
        if debug and parser:
            print('stack of symbols:', parser.symstack)
            print('next token:', parser.token())
        raise SyntaxError('Unexpected end of file')

    if parser is None:
        raise SyntaxError('unexpected token: %r' % p)

    raise SyntaxError('unexpected token: %r' % p)


def make_rule_handler(rule, handler):
    """
    Convert a handler function func(*args) -> AST into a rule that uses the PLY
    interface such as::

        def p_rule_name(p):
            "<rule>"

            p[0] = func(*p[1:])
    """

    has_omissions = '~' in rule
    if '~' in rule and '|' in rule:
        msg = 'cannot omit symbols in an OR rule:\n    ' + rule
        raise ValueError(msg)

    body = rule.partition(':')[-1].strip()
    keep_list = list(map(lambda x: not x.startswith('~'), body.split()))
    doc = rule.replace('~', '')

    def rule_handler(p):
        _, *args = p
        if has_omissions:
            args = (x for x, keep in zip(args, keep_list) if keep)
        try:
            p[0] = handler(*args)
        except Exception as ex:
            msg = [str(ex), '    Raised when handling rule:\n', ' ' * 8 + rule]
            raise type(ex)('\n'.join(msg))

    rule_handler.__doc__ = doc
    return rule_handler


def requires_empty_rule(rules):
    """
    Return True if the list of rules contain a rule that uses the "empty"
    symbol.
    """

    for rule, _ in rules:
        rhs = rule.partition(':')[-1].split()
        if 'empty' in rhs:
            return True
    return False


def get_token_list(rules):
    """
    Return a list of tokens used on the given list of rules.
    """

    tokens = set()
    for rule, handler in rules:
        tokens.update(FINAL_TOKEN_NAME.findall(rule))
    return sorted(tokens)


def simplify_rules(rules):
    """
    Receive a list of rules and breaks all OR rules into separate lines.
    """

    for rule, handler in rules:
        if '|' in rule:
            rule = rule.replace('\n|', '|').replace('|', '\n|')
        if handler is ...:
            lhs, _, rhs = rule.partition(':')
            yield rule, sexpr_handler(lhs.strip())
        else:
            yield rule, handler


def sexpr_handler(name):
    """
    A handler function created for the ellipsis (...) handler.
    """

    return lambda *args: (name,) + args


def get_caller_file():
    """
    Return the path of the caller.
    """
    return os.getcwd()


class Logger(yacc.PlyLogger):
    def debug(self, msg, *args, **kwargs):
        pass
