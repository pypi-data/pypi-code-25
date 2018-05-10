from functools import singledispatch
from inspect import Signature
from typing import Optional

from sidekick import Union, opt, identity
from .ast_expr import Expr, as_expr
from .ast_types import Symbol, ListOf, DictOf, AtomType
from .operators import Inplace
from .utils import item_getter

this = object


class DescriptorMeta(type):
    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        else:
            return self(instance)


class Statement(Union):
    """
    Represent Python statements.
    """

    # Definitions
    ClassDef = opt([
        ('name', Symbol),
        ('bases', ListOf[Expr]),
        ('options', DictOf[Symbol, Expr]),
        ('body', ListOf[this]),
    ])
    FuncDef = opt([
        ('name', Symbol),
        ('fargs', ListOf[Symbol]),
        ('body', ListOf[this]),
    ])
    FuncDefFull = opt([
        ('name', Symbol),
        ('signature', Signature),
        ('body', ListOf[this]),
    ])

    # Simple statements
    Assign = opt([
        ('lhs', Expr),
        ('rhs', Expr),
    ])
    Break = opt()
    Continue = opt()
    Del = opt(Expr)
    ExprStmt = opt(Expr)
    OpAssign = opt([
        ('op', Inplace),
        ('lhs', Expr),
        ('rhs', Expr),
    ])
    Pass = opt()
    Return = opt(Expr)
    Yield = opt([
        ('value', Expr),
        ('target', Optional[Symbol]),
    ])
    YieldFrom = opt([
        ('value', Expr),
        ('target', Optional[Symbol]),
    ])

    # Control flow and compound statements
    If = opt([
        ('cond', Expr),
        ('then', ListOf[this]),
        ('other', ListOf[this]),
    ])
    For = opt([
        ('var', Expr),
        ('seq', Expr),
        ('body', ListOf[this]),
        ('other', ListOf[this]),
    ])
    While = opt([
        ('cond', Expr),
        ('body', ListOf[this]),
        ('other', ListOf[this]),
    ])
    With = opt([
        ('value', Expr),
        ('name', Optional[Symbol]),
        ('body', ListOf[this]),
    ])
    Block = opt(data=ListOf[this])

    # Imports
    Import = opt([
        ('module', str),
    ])
    ImportFrom = opt([
        ('module', str),
        ('names', dict),
    ])

    def source(self):
        """
        Return a source code representation of statement.
        """
        from .printers import source
        return source(self)

    def print_source(self, file=None, end='\n'):
        """
        Print source for the current statement.
        """
        print(self.source(), file=file, end=end)

    class elif_(metaclass=DescriptorMeta):  # noqa: N801
        """
        Return a copy of statement with an attached elif block.
        """

        def __init__(self, obj):
            if not isinstance(obj, If):
                raise TypeError('only if statements accept an elif clause')
            self._obj = obj

        def _add_elif(self, cond, block):
            obj = self._obj
            if_cond, if_then, if_other = obj.args

            if obj.has_elif:
                new_elif = If(*if_other[0].args).elif_(cond, block)
                return If(if_cond, if_then, [new_elif])
            else:
                elif_block = If(as_expr(cond), stmt_list(block), if_other)
                return If(if_cond, if_then, [elif_block])

        def __call__(self, cond, block=None):
            if block is None:
                return item_getter(lambda block: self._add_elif(cond, block))
            else:
                return self._add_elif(cond, block)

    class else_(metaclass=DescriptorMeta):  # noqa: N801
        """
        Return a copy of statement with an attached else block.
        """

        def __init__(self, obj):
            if not isinstance(obj, (If, For, While)):
                msg = '%s statements do not have an else clause'
                raise TypeError(msg % type(self).__name__)
            self._obj = obj

        def __call__(self, block):
            obj = self._obj

            if obj.has_elif:
                cond, then, other = obj.args
                if else_block_is_elif(other):
                    block = [other[0].else_(block)]
                else:
                    block = stmt_list(block)
                return If(cond, then, block)
            else:
                args = obj.args
                new_args = args[:-1] + (stmt_list(block),)
                return type(obj)(*new_args)

        def __getitem__(self, item):
            return self(item)


#
# Case-specific properties
#
Statement.If.has_elif = property(
    lambda self:
    else_block_is_elif(self.other) if isinstance(self, If) else False
)


def else_block_is_elif(other):
    return len(other) == 1 and isinstance(other[0], If)


# Aliases
Assign = Statement.Assign
Block = Statement.Block
Break = Statement.Break
ClassDef = Statement.ClassDef
Continue = Statement.Continue
Del = Statement.Del
ExprStmt = Statement.ExprStmt
For = Statement.For
FuncDefFull = Statement.FuncDefFull
FuncDef = Statement.FuncDef
If = Statement.If
Import = Statement.Import
ImportFrom = Statement.ImportFrom
OpAssign = Statement.OpAssign
Pass = Statement.Pass
Return = Statement.Return
While = Statement.While
With = Statement.With
Yield = Statement.Yield
YieldFrom = Statement.YieldFrom


#
# Utilities
#
@singledispatch
def as_stmt(body):
    """
    Convert element to a Statement instance.
    """
    raise TypeError


as_stmt.register(Statement)(identity)
as_stmt.register(Expr)(ExprStmt)


@as_stmt.register(tuple)
@as_stmt.register(list)
@as_stmt.register(type(_ for _ in ()))
def _(x):
    return Block(list(map(as_stmt, x)))


for _tt in AtomType.__args__:
    as_stmt.register(_tt)(lambda x: ExprStmt(as_expr(x)))


@as_expr.register(ExprStmt)
def _(obj):
    msg = 'Python statement cannot be converted to expresssion: %r' % obj
    raise TypeError(msg)


def stmt_list(obj):
    """
    Convert obj into a list of statements.

    Block -> obj.data
    Statement -> [obj]
    List or tuple -> list(obj)
    Other -> [stmt(obj)]
    """
    if isinstance(obj, Block):
        return obj.data
    elif isinstance(obj, Statement):
        return [obj]
    elif isinstance(obj, (list, tuple)):
        return list(map(as_stmt, obj))
    else:
        return [as_stmt(obj)]
