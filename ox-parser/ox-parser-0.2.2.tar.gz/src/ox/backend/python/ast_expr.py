from functools import singledispatch
from inspect import Signature

from .ast_types import Symbol, AtomType, ListOf, CallArgs, DictOf
from .operators import Op, Unary
from ...union import Union, opt


def mk_expr_binary_op(op, right=False):
    """
    Return a function that implements a binary operator for the given
    expression.
    """

    def operator(self, other):
        other = as_expr(other)
        self = as_expr(self)
        return BinOp(op, self, other)

    if right:
        return lambda x, y: operator(y, x)
    return operator


this = object


class Expr(Union):
    """
    Represents Python expression nodes.
    """

    # Atoms and literal data structures
    Atom = opt(value=AtomType)
    Name = opt(Symbol)
    Tuple = opt(ListOf[this])
    List = opt(ListOf[this])
    Set = opt(ListOf[this])
    Dict = opt(ListOf[tuple])

    # Lambdas
    Lambda = opt([
        ('fargs', ListOf[Symbol]),
        ('body', this),
    ])
    FullLambda = opt([
        ('signature', Signature),
        ('body', this),
    ])

    # Operators and function calls
    UnaryOp = opt([
        ('op', Unary),
        ('data', this),
    ])
    BinOp = opt([
        ('op', Op),
        ('lhs', this),
        ('rhs', this),
    ])
    GetAttr = opt([
        ('value', this),
        ('attr', Symbol),
    ])
    GetItem = opt([
        ('value', this),
        ('index', this),
    ])
    Call = opt([
        ('caller', this),
        ('fargs', ListOf[this]),
        ('kwargs', DictOf[str, this])
    ])
    FullCall = opt(
        ('caller', this),
        ('fargs', CallArgs),
    )

    # Control flow
    IfExpr = opt([
        ('cond', this),
        ('then', this),
        ('other', this),
    ])
    AndExpr = opt([
        ('lhs', this),
        ('rhs', this),
    ])
    OrExpr = opt([
        ('lhs', this),
        ('rhs', this),
    ])
    NotExpr = opt(this)

    # Comprehensions
    ListComp = opt([
        ('item', this),
        ('vars', this),
        ('seq', this),
        ('cond', this),
    ])
    SetComp = opt([
        ('item', this),
        ('vars', this),
        ('seq', this),
        ('cond', this),
    ])
    Generator = opt([
        ('item', this),
        ('vars', this),
        ('seq', this),
        ('cond', this),
    ])
    DictComp = opt([
        ('key', this),
        ('value', this),
        ('vars', this),
        ('seq', this),
        ('cond', this),
    ])

    # Arithmetic operators
    __add__ = mk_expr_binary_op(Op.ADD)
    __sub__ = mk_expr_binary_op(Op.SUB)
    __mul__ = mk_expr_binary_op(Op.MUL)
    __matmul__ = mk_expr_binary_op(Op.MATMUL)
    __mod__ = mk_expr_binary_op(Op.MOD)
    __truediv__ = mk_expr_binary_op(Op.TRUEDIV)
    __floordiv__ = mk_expr_binary_op(Op.FLOORDIV)
    __pow__ = mk_expr_binary_op(Op.POW)
    __radd__ = mk_expr_binary_op(Op.ADD, right=True)
    __rsub__ = mk_expr_binary_op(Op.SUB, right=True)
    __rmul__ = mk_expr_binary_op(Op.MUL, right=True)
    __rmatmul__ = mk_expr_binary_op(Op.MATMUL, right=True)
    __rmod__ = mk_expr_binary_op(Op.MOD, right=True)
    __rtruediv__ = mk_expr_binary_op(Op.TRUEDIV, right=True)
    __rfloordiv__ = mk_expr_binary_op(Op.FLOORDIV, right=True)
    __rpow__ = mk_expr_binary_op(Op.POW, right=True)

    # Comparison operators
    __gt__ = mk_expr_binary_op(Op.GT)
    __lt__ = mk_expr_binary_op(Op.LT)
    __ge__ = mk_expr_binary_op(Op.GE)
    __le__ = mk_expr_binary_op(Op.LE)

    # Bitwise operators
    __or__ = mk_expr_binary_op(Op.OR)
    __xor__ = mk_expr_binary_op(Op.XOR)
    __and__ = mk_expr_binary_op(Op.AND)
    __rshift__ = mk_expr_binary_op(Op.RSHIFT)
    __lshift__ = mk_expr_binary_op(Op.LSHIFT)
    __ror__ = mk_expr_binary_op(Op.OR, right=True)
    __rxor__ = mk_expr_binary_op(Op.XOR, right=True)
    __rand__ = mk_expr_binary_op(Op.AND, right=True)
    __rrshift__ = mk_expr_binary_op(Op.RSHIFT, right=True)
    __rlshift__ = mk_expr_binary_op(Op.LSHIFT, right=True)

    # Unary operators
    def __pos__(self):
        return UnaryOp(Unary.POS, self)

    def __neg__(self):
        return UnaryOp(Unary.NEG, self)

    def __not__(self):
        return UnaryOp(Unary.NOT, self)

    # Other special methods
    def __getitem__(self, index):
        return GetItem(self, index)

    def __call__(self, *args, **kwargs):
        args = [as_expr(x) for x in args]
        kwargs = {Symbol(k): as_expr(v) for k, v in kwargs.items()}
        return Expr.Call(self, args, kwargs)

    #
    # API
    #
    def attr(self, attr):
        """
        Return an expression node equivalent of ``self.<attr>``.
        """
        return GetAttr(self, Symbol(attr))

    def method(self, method, *args, **kwargs):
        """
        Return an expression node equivalent to a method call with the given
        arguments.
        """
        return self.attr(method)(*args, **kwargs)

    def equal(self, other):
        """
        Create a new expression node representing ``self == other``.
        """
        return equal(self, other)

    def not_equal(self, other):
        """
        Create a new expression node representing ``self != other``.
        """
        return not_equal(self, other)

    def source(self):
        """
        Return a string of Python source code representing the expr object.
        """
        from .printers import expr_source
        return expr_source(self)


# Aliases
Atom = Expr.Atom
AndExpr = Expr.AndExpr
BinOp = Expr.BinOp
Call = Expr.Call
Dict = Expr.Dict
DictComp = Expr.DictComp
FullCall = Expr.FullCall
FullLambda = Expr.FullLambda
Generator = Expr.Generator
GetAttr = Expr.GetAttr
GetItem = Expr.GetItem
IfExpr = Expr.IfExpr
Lambda = Expr.Lambda
List = Expr.List
ListComp = Expr.ListComp
Name = Expr.Name
NotExpr = Expr.NotExpr
OrExpr = Expr.OrExpr
Set = Expr.Set
SetComp = Expr.SetComp
Tuple = Expr.Tuple
UnaryOp = Expr.UnaryOp


#
# Utility functions
#
@singledispatch
def as_expr(obj):
    """
    Convert object to an Expr node, if possible.
    """
    raise TypeError('cannot be converted to python expr: %r' % obj)


as_expr.register(Expr)(lambda x: x)
for _tt in AtomType.__args__:
    as_expr.register(_tt)(Atom)

_seq_handler = (lambda cls: lambda data: cls(list(map(as_expr, data))))
for _py_cls, _cls in [(list, List), (tuple, Tuple), (set, Set)]:
    as_expr.register(_py_cls)(_seq_handler(_cls))

as_expr.register(dict)(
    lambda data: Dict([(as_expr(x), as_expr(y)) for x, y in data.items()]))

equal = mk_expr_binary_op(Op.EQ)
not_equal = mk_expr_binary_op(Op.NE)
