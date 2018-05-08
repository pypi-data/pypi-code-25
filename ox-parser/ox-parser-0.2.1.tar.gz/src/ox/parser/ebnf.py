import collections
import re
import tokenize
import typing
from collections import deque

from sidekick import fn
from .ebnf_expr import Hidden, Optional
from .ebnf_expr import Name, Token, Literal, Or, Sequence, Repeat, RepeatOne
from .ply import ply_parser
from ..helpers import cons, pair, clean_string, identity, args
from ..helpers import first, second
from ..lexer import make_lexer


def ebnf_parser(rules, start=None, *, debug=True):
    """
    Return a parser function from a set of rules written in a EBNF grammar.
    """

    ebnf_parser = EBNFParser(rules)
    bnf_rules = ebnf_parser.to_bnf_rules()
    bnf_parser = ply_parser(bnf_rules, start=start, debug=debug)
    fix_tokens = ebnf_parser.transform_tokens

    def parser(tokens: typing.Iterable):
        """
        Parse sequence of tokens.
        """

        tokens = fix_tokens(tokens)
        return bnf_parser(tokens)

    return parser


class EBNFParser(collections.Sequence):
    """
    A EBNF parser that convert rules to a BNF syntax that PLY can understand.

    It is modelled as a list of rules.
    """

    def __init__(self, rules, memo=None):
        self.rules = rules = list(rules)

        # Parse all rules and replace literals with their corresponding token
        # names
        self.tk_memo = tk_memo = dict(memo or {})
        self.clean_rules = []

        for rule, func in rules:
            try:
                name, expr = parse_ebnf(rule)
            except SyntaxError:
                msg = 'invalid rule: %r' % rule
                raise SyntaxError(msg)
            expr = expr.to_token(tk_memo)
            self.clean_rules.append(((name, expr), func))

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def __getitem__(self, i):
        return self.rules[i]

    def to_bnf(self):
        """
        Convert a EBNF grammar to a simple BNF grammar.
        """
        return EBNFParser(self.to_bnf_rules(), memo=self.tk_memo)

    def to_bnf_rules(self):
        """
        Convert list of rules to a BNF compatible list of rules.

        Returns a list of (rule, handler) pairs.
        """

        rules = deque(self.clean_rules)
        rule_names = set()
        converted = []

        while rules:
            (name, expr), func = rules.popleft()
            for name, expr, handler in expr.to_simple(name, func, rule_names):
                expr = expr.normalize_names()
                rule = '%s : %s' % (name, expr.source())
                converted.append((rule, handler))
        return converted

    def transform_tokens(self, tokens):
        """
        Convert a stream of tokens to the correct token types by converting
        literal values to the proper tokens.
        """

        memo = self.tk_memo
        for tk in tokens:
            if tk.value in memo:
                tk_type = memo[tk.value]
                yield tk.copy(type=tk_type)
            else:
                yield tk


#
# EBNF rules lexer
#
lexer_rules = [
    ('NAME', r'[_a-z][_a-z0-9]*'),
    ('TOK_NAME', r'[_A-Z][_A-Z0-9]*'),
    ('LITERAL', "'" + tokenize.Single),
    ('BACKTICK', ("'" + tokenize.Single).replace("'", '`')),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACK', r'\['),
    ('RBRACK', r'\]'),
    ('PIPE', r'\|'),
    ('TIMES', r'\*'),
    ('PLUS', r'\+'),
    ('TILDE', r'\~'),
    ('COLON', r':'),
]
ebnf_grammar_lexer = make_lexer(lexer_rules)

#
# EBNF rules parser
#
OPEN_BACKTICK = re.compile(r'^`')
CLOSE_BACKTICK = re.compile(r'`$')


def to_sequence(constructor):
    def func(x, y):
        if isinstance(y, constructor):
            return constructor(cons(x, y.data))
        else:
            return constructor(pair(x, y))

    return func


@fn
def clean_backtick(data):
    return clean_string(data, open=OPEN_BACKTICK, close=CLOSE_BACKTICK)


parser_rules = [
    ('definition : NAME ~COLON expr', args),

    # Pipe expressions
    ('expr : term ~PIPE expr', to_sequence(Or)),
    ('expr : term', identity),

    # Sequence of values
    ('term : simple term', to_sequence(Sequence)),
    ('term : simple', identity),

    # Simple modifiers
    ('simple : atom TIMES', first >> Repeat),
    ('simple : atom PLUS', first >> RepeatOne),
    ('simple : TILDE atom', second >> Hidden),
    ('simple : atom', identity),

    # Atomic types
    ('atom : LPAREN expr RPAREN', second),
    ('atom : LBRACK expr RBRACK', second >> Optional),
    ('atom : NAME', Name),
    ('atom : TOK_NAME', Token),
    ('atom : LITERAL', clean_string >> Literal >> Hidden),
    ('atom : BACKTICK', clean_backtick >> Literal),
]
ebnf_grammar_parser = fn(ply_parser(parser_rules))
parse_ebnf = ebnf_grammar_lexer >> ebnf_grammar_parser
