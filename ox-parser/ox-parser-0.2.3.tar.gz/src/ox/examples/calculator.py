import operator as op

import ox
from ox.helpers import identity

op_map = {'+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv, '^': op.pow}
binop = (lambda x, op, y: (op, x, y))

# Lexer
lexer = ox.make_lexer([
    ('NUMBER', r'\d+(\.\d*)?'),
    ('OP', r'[-+*/^]'),
    ('SYMBOLS', r'[()]'),
])

# Parser
parser = ox.make_parser([
    ("expr : expr (`+` | `-`) term", binop),
    ("expr : term", identity),

    ("term : term (`*` | `/`) power", binop),
    ("term : power", identity),

    ("power : atom `^` power", binop),
    ("power : atom", identity),

    ("atom : NUMBER", float),
    ("atom : '(' expr ')'", identity),
])


def eval_ast(ast):
    if isinstance(ast, tuple):
        func, *args = ast
        func = op_map[func]
        return func(*map(eval_ast, args))
    else:
        return ast


eval = lexer >> parser >> eval_ast
