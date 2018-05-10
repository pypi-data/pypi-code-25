from inspect import Parameter, Signature

from .ast_expr import IfExpr, Name, Expr
from .ast_expr import as_expr, equal, not_equal
from .ast_statement import (
    Assign, Block, Del, FuncDef, If, Import, ImportFrom, OpAssign, Pass, Return,
    While, With, Yield, as_stmt)
from .ast_statement import stmt_list
from .ast_types import Symbol
from .operators import INPLACE_OPERATORS
from .utils import make_instance, item_getter

__all__ = [
    'as_expr', 'equal', 'not_equal', 'attr', 'var', 'cond',
    'let', 'function'
]


#
# Expressions
#
def attr(x, y):
    """
    Alias to x.attr(y) <==> Creates an attribute access expression node.
    """
    return x.attr(y)


@make_instance
class var:  # noqa: N801
    """
    Creates a Python variable object:

        var.x <==> var('x') <==> Expr.Name(Symbol('x')))

    """

    def __call__(self, attr):
        if ',' in attr:
            attrs = map(str.strip, attr.split(','))
            return [self(x) for x in attrs]
        return Name(Symbol(attr))

    def __getattr__(self, name):
        return self(name)


@make_instance
class symb:  # noqa: N801
    """
    Creates a Pythhn symbol object:

        symb.x <==> symb('x') <==> Symbol('x')

    """

    def __call__(self, attr):
        if ',' in attr:
            attrs = map(str.strip, attr.split(','))
            return [self(x) for x in attrs]
        return Symbol(attr)

    def __getattr__(self, name):
        return self(name)


def signature(*args, **kwargs):
    """
    Create a signature object representing a function definition.
    """
    kind = Parameter.POSITIONAL_ONLY
    params = []

    for arg in args:
        if isinstance(arg, (str, Symbol)):
            if arg == '*':
                kind = Parameter.KEYWORD_ONLY
                continue
            param = Parameter(str(arg), kind=kind)
        elif isinstance(arg, (str, Name)):
            param = Parameter(str(arg.value), kind=kind)
        else:
            raise TypeError(arg)
        params.append(param)

    if kind == Parameter.POSITIONAL_ONLY:
        kind = Parameter.POSITIONAL_OR_KEYWORD
    for name, value in kwargs.items():
        value = as_expr(value)
        param = Parameter(name, default=value, kind=kind)
        params.append(param)

    return Signature(params)


class lambd:
    """
    Creates a lambda expression.

        lambd('x', y=42)[var.x + var.y] <==> lambda x, y: x + y
    """

    def __init__(self, *args, **kwargs):
        self.args = [as_symbol(x) for x in args]
        self.kwargs = {k: as_expr(v) for k, v in kwargs.items()}

    def __getitem__(self, value):
        if not self.kwargs:
            return Expr.Lambda(self.args, as_expr(value))
        else:
            sig = signature(*self.args, **self.kwargs)
            return Expr.FullLambda(sig, value)


def cond(value, *, if_, else_):
    """
    Creates a Python if expression of the form "<value> if <if_> else <else_>"

    Usage:
        >>> cond(var.x + 1, if_=var.x, else_=0)
        IfExpr(Var('x'), Op(..))

    Args:
        value:
            The default value expression.
        if_:
            The condition expression.
        else_:
            The alternate expression.

    Returns:
        A Expr.IfExpr value.
    """
    return IfExpr(as_expr(if_), as_expr(value), as_expr(else_))


def expr_or_name(x):
    """
    Like expr(), but coerce strings to Name instead of Atom.
    """
    if isinstance(x, str):
        return Name(Symbol(x))
    return as_expr(x)


def as_symbol(x):
    """
    Coerce object to symbol
    """
    if isinstance(x, Symbol):
        return x
    elif isinstance(x, str):
        return Symbol(x)
    elif isinstance(x, Name):
        return x.value
    else:
        raise TypeError('cannot convert to symbol: %r' % x)


#
# Statements
#
def let(*args, **kwargs):
    """
    Create one or more variable assignment statements:

    let(x=expr)
    let(lhs, rhs)
    """
    if args and not kwargs:
        return assign(*args)
    elif args:
        assignments = [assign(*args)]
    else:
        assignments = []

    for k, v in kwargs.items():
        assignments.append(assign(k, v))

    if len(assignments) == 1:
        return assignments[0]
    elif len(assignments) == 0:
        return pass_
    else:
        return block(assignments)


def assign(*args):
    """
    Complex assignment
    """

    if len(args) == 2:
        lhs, rhs = args
        return Assign(expr_or_name(lhs), as_expr(rhs))
    elif len(args) == 3:
        lhs, op, rhs = args
        op = INPLACE_OPERATORS.get(op, op)
        return OpAssign(op, expr_or_name(lhs), as_expr(rhs))
    else:
        raise TypeError('must be called with exactly 2 or 3 arguments')


@make_instance
class function:  # noqa: N801
    """
    Creates a Stmt node representing a Python def block.

    function.foo(arg1, arg2)[
        stmt1,
        stmt2,
        ...,
    ]
    """

    def __func(self, name, args, body):
        if not isinstance(body, (tuple, list)):
            body = body,
        body = list(body)
        return FuncDef(as_symbol(name), [as_symbol(x) for x in args], body)

    def __call__(self, name, fargs, body):
        return self[name](*fargs)[body]

    def __getattr__(self, attr):
        return lambda *args: item_getter(
            lambda body: self.__func(attr, args, body))

    def __getitem__(self, item):
        return self.__getattr__(item)


class if_:  # noqa: N801
    """
    Creates a Stmt node representing a Python if block.

    if_(cond1)[
        stmt1,
        ...,
    ].elif_(cond2)[
        stmt2,
        ...,
    ]
    .else_[
        stmt3,
        ...,
    ]
    """

    def __new__(cls, cond, then=None, else_=None):
        if then is not None:
            return If(as_expr(cond), stmt_list(then), stmt_list(else_ or []))
        return super().__new__(cls)

    def __init__(self, cond, then=None, else_=None):
        self._cond = as_expr(cond)
        if else_ is not None:
            msg = 'then clause cannot be None if else clause is given'
            raise TypeError(msg)

    def __getitem__(self, item):
        return If(self._cond, stmt_list(item), [])


def for_(name, expr):
    """
    Creates a Stmt node representing a Python for block.

    for_(name, expr)[
        stmt1,
        ...,
    ].else_[
        stmt2,
        ...,
    ]
    """
    raise NotImplementedError


def while_(cond, body=None):
    """
    Creates a Stmt node representing a Python while block.

    while_(expr)[
        stmt1,
        ...,
    ].else_[
        stmt2,
        ...,
    ]
    """
    if body is not None:
        return while_(cond)[tuple(body)]

    cond = as_expr(cond)
    return item_getter(lambda body: While(cond, stmt_list(body), []))


def try_():
    """
    Creates a Stmt node representing a Python try block.

    try_[
        stmt1,
        ...,
    ].except_(exception, var)[
        stmt2,
        ...,
    ].finally_[
        stmt3,
        ...,
    ]
    """
    raise NotImplementedError


def with_(obj, as_=None, body=None):
    """
    Creates a Stmt node representing a Python with block.

    with_(obj, varname)[
        stmt1,
        stmt2,
        ...,
    ]
    """
    if body is not None:
        return with_(as_expr, as_=as_)[tuple(body)]

    obj = as_expr(obj)
    return item_getter(lambda body: With(obj, as_, stmt_list(body), []))


def class_():
    """
    Creates a Stmt node representing a Python class definition block.

    class.ClassName(expr)[
        stmt1,
        stmt2,
        ...,
    ]
    """
    raise NotImplementedError


def import_from(module, vars=None, **kwargs):
    """
    Import names from a module.

    import_from('math')  <==> import math
    import_from('math', ['sqrt'])  <==> from math import sqrt
    import_from('math', {'sqrt': 'f'})  <==> from math import sqrt as f
    import_from('math', sqrt='f')  <==> from math import sqrt as f
    """
    if not vars and not kwargs:
        return Import(module)

    if hasattr(vars, 'items'):
        kwargs.update(vars)
    elif vars is not None:
        return import_from(module, {k: k for k in vars}, **kwargs)
    return ImportFrom(module, kwargs)


# Simple statements
del_ = (lambda x: Del(as_expr(x)))
return_ = (lambda x: Return(as_expr(x)))
yield_ = (lambda x: Yield(as_expr(x)))
block = (lambda x: Block(list(map(as_stmt, x))))
pass_ = Pass
