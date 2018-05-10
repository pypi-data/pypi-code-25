import io
from functools import singledispatch

from sidekick import casedispatch
from .ast_expr import Expr, BinOp, UnaryOp, IfExpr
from .ast_statement import Statement, If
from .operators import PRECEDENCE
from ...utils import interspace


class Context:
    """
    A context object that controls how code is emitted.
    """

    def __init__(self, file=None, indentation=0):
        self.file = io.StringIO() if file is None else file
        self.indentation = indentation

    def write(self, *args):
        """
        Write string data into the current file.
        """
        for arg in args:
            self.file.write(arg)

    def write_indent(self, *args):
        """
        Writes the current indentation level.
        """
        self.write(' ' * (4 * self.indentation))
        if args:
            self.write(*args)


def source(obj, indentation=0):
    """
    Return a string representation of expression node.

    Args:
        obj:

    Usage:
        >>> source(var.x + 1)
        'x + 1'
    """
    ctx = Context(indentation=indentation)
    emit(obj, ctx)
    return ctx.file.getvalue()


#
# Emit code for Expr and Statement objects
#
@singledispatch
def emit(obj, ctx):
    """
    Emit code for the given expression node and context.

    Args:
        obj:
            Expression node
        ctx:
            A context object with variables that control code emission
            context.

    Returns:
    """
    raise TypeError('cannot emit code for %s' % type(obj).__name__)


@emit.register(Expr)
def emit_expr(x, ctx):
    ctx.write(expr_source(x))


#
# Declare statement printers
#
# noinspection PyPep8Naming,PyMethodParameters
@emit.register(Statement)
@casedispatch.from_namespace(Statement)
class emit_stmt:  # noqa: N801
    # Definitions
    def ClassDef(*args):  # noqa: N802, N805
        raise NotImplementedError

    def FuncDef(name, fargs, body, ctx):  # noqa: N802, N805
        args = ', '.join(fargs)
        ctx.write_indent('def %s(%s):\n' % (name, args))
        write_block(body, ctx)

    def FuncDefFull(*args):  # noqa: N802, N805
        raise NotImplementedError

    # Simple statements
    def Assign(lhs, rhs, ctx):  # noqa: N802, N805
        ctx.write_indent(lhs.source(), ' = ', rhs.source())

    def Break(ctx):  # noqa: N802, N805
        ctx.write_indent('break')

    def Continue(ctx):  # noqa: N802, N805
        ctx.write_indent('continue')

    def Del(ctx, data):  # noqa: N802, N805
        ctx.write_indent('del ', interspace(',', map(source, data)))

    def ExprStmt(expr, ctx):  # noqa: N802, N805
        ctx.write_indent(expr_source(expr))

    def OpAssign(op, lhs, rhs, ctx):  # noqa: N802, N805
        ctx.write_indent()
        ctx.write(lhs.source(), ' ', op.value, ' ', rhs.source())

    def Pass(ctx):  # noqa: N802, N805
        ctx.write_indent('pass')

    def Return(expr, ctx):  # noqa: N802, N805
        ctx.write_indent('return ', expr_source(expr))

    def Yield(expr, ctx):  # noqa: N802, N805
        ctx.write_indent('yield ', expr_source(expr))

    def YieldFrom(expr, ctx):  # noqa: N802, N805
        ctx.write_indent('yield from ', expr_source(expr))

    # Control flow and compound statements
    def If(cond, then, other, ctx):  # noqa: N802, N805
        ctx.write_indent('if ', expr_source(cond), ':\n')
        write_block(then, ctx)

        while other:
            # Nested ifs are converted to elifs
            if len(other) == 1 and isinstance(other[0], If):
                cond_, then, other = other[0].args
                ctx.write_indent('\nelif ', expr_source(cond_), ':\n')
                write_block(then, ctx)
            else:
                ctx.write_indent('\nelse:\n')
                write_block(other, ctx)
                other = None

    def For(var, seq, body, else_, ctx):  # noqa: N802, N805
        src = expr_source
        ctx.write_indent('for ', src(var), ' in ', src(seq), ':\n')
        write_block_with_else(body, else_, ctx)

    def While(cond, body, else_, ctx: Context):  # noqa: N802, N805
        ctx.write_indent('while ', expr_source(cond), ':\n')
        write_block_with_else(body, else_, ctx)

    def With(value, as_, body, ctx):  # noqa: N802, N805
        ctx.write_indent('with ', expr_source(value))
        if as_ is not None:
            ctx.write(' as ', expr_source(as_), ':\n')
        else:
            ctx.write(':\n')
        write_block(body, ctx)

    def Block(data, ctx):  # noqa: N802, N805
        write_block(data, ctx, indent_delta=0)

    # Imports
    def Import(module, ctx):  # noqa: N802, N805
        ctx.write_indent('import ', module)

    def ImportFrom(module, names, ctx):  # noqa: N802, N805
        data = []
        for k, v in names.items():
            if k == v:
                data.append(k)
            else:
                data.append('%s as %s' % (k, v))
        import_names = ', '.join(data)
        ctx.write_indent('from %s import %s' % (module, import_names))


def write_block(stmts: list, ctx: Context, indent_delta=1):
    try:
        ctx.indentation += indent_delta
        if not stmts:
            ctx.write_indent('pass')
        else:
            line_ends = ['\n' for _ in stmts]
            line_ends[-1] = ''
            for stmt, end in zip(stmts, line_ends):
                emit_stmt(stmt, ctx)
                ctx.write(end)
    finally:
        ctx.indentation -= indent_delta


def write_block_with_else(stms, else_, ctx):
    write_block(stms, ctx)
    if else_:
        ctx.write_indent('else:\n')
        write_block(else_, ctx)


#
# Print code for Expr nodes
#
# noinspection PyPep8Naming,PyMethodParameters
@casedispatch.from_namespace(Expr)
class expr_source:  # noqa: N801
    """
    Return a source code string for the given expression node.
    """

    # Basic data types and containers
    def Atom(x):  # noqa: N802, N805
        if isinstance(x, (int, float)) and x < 0:
            return '(%r)' % x
        return repr(x)

    def Name(name):  # noqa: N802, N805
        return str(name)

    def Dict(data):  # noqa: N802, N805
        src = expr_source
        data = ', '.join('%s: %s' % (src(k), src(v)) for k, v in data)
        return '{%s}' % data

    def List(data):  # noqa: N802, N805
        return linear_container(data, '[]')

    def Set(data):  # noqa: N802, N805
        if not data:
            return 'set()'
        return linear_container(data, '{}')

    def Tuple(data):  # noqa: N802, N805
        if len(data) == 1:
            return '(%s,)' % expr_source(data[0])
        return linear_container(data, '()')

    # Operators
    def BinOp(op, lhs, rhs):  # noqa: N802, N805
        # Check precedence and associativity to see if expression requires
        # parenthesis in any of is arguments
        precedence = PRECEDENCE[op]

        def wrap_parens(x):
            src = expr_source(x)
            require_parens = False
            if isinstance(x, BinOp) and PRECEDENCE[x.op] <= precedence:
                require_parens = True
            elif isinstance(x, (UnaryOp, IfExpr)):
                require_parens = True
            return '(%s)' % src if require_parens else src

        x = wrap_parens(lhs)
        y = wrap_parens(rhs)
        return '%s %s %s' % (x, repr_op(op), y)

    def UnaryOp(op, x):  # noqa: N802, N805
        return '%s%s' % (repr_op(op), expr_source(x))

    def GetAttr(value, attr):  # noqa: N802, N805
        return '%s.%s' % (expr_source(value), attr)

    def GetItem(value, item):  # noqa: N802, N805
        return '%s[%s]' % (expr_source(value), expr_source(item))

    # Functions
    def Call(func, args, kwargs):  # noqa: N802, N805
        src = expr_source
        argdata = ', '.join(map(src, args))
        kwitems = ((str(k), src(v)) for k, v in kwargs.items())
        kwdata = ', '.join('%s=%s' % item for item in kwitems)
        return '{caller}({argdata})'.format(
            caller=src(func),
            argdata=', '.join([x for x in [argdata, kwdata] if x]),
        )

    def FullCall(func, argspec):  # noqa: N802, N805
        raise NotImplementedError

    def Lambda(args, body):  # noqa: N802, N805
        return 'lambda {args}: {body}'.format(
            args=', '.join(map(str, args)),
            body=expr_source(body),
        )

    def FullLambda(argspec, body):  # noqa: N802, N805
        return 'lambda {args}: {body}'.format(
            args=argspec.source(),
            body=expr_source(body),
        )

    def IfExpr(cond, then, other):  # noqa: N802, N805
        args = map(expr_source, [then, cond, other])
        return '({} if {} else {})'.format(*args)

    def AndExpr(*args):  # noqa: N802, N805
        return '{} and {}'.format(*map(expr_source, args))

    def OrExpr(*args):  # noqa: N802, N805
        return '{} or {}'.format(*map(expr_source, args))

    def NotExpr(value):  # noqa: N802, N805
        return 'not {}'.format(expr_source(value))

    # Comprehensions
    def ListComp(*args):  # noqa: N802, N805
        return simple_comprehension('[]', args)

    def Generator(*args):  # noqa: N802, N805
        return simple_comprehension('()', args)

    def SetComp(*args):  # noqa: N802, N805
        return simple_comprehension('{}', args)

    def DictComp(*args):  # noqa: N802, N805
        # Check the "if" argument (which is the last one)
        if args[-1] is None:
            data = '{}: {} for {} in {}'.format(*args[:-1])
        else:
            data = '{}: {} for {} in {} if {}'.format(*args)
        return '{%s}' % data

    # Other
    def else_(x):  # noqa: N805
        raise NotImplementedError('invalid type: %s' % x)


def simple_comprehension(parens, args):
    open, close = parens

    # Check the "if" argument (which is the last one)
    if args[-1] is None:
        data = '{} for {} in {}'.format(*args[:-1])
    else:
        data = '{} for {} in {} if {}'.format(*args)
    return '%s%s%s'.format(open, data, close)


def linear_container(data: list, parens):
    open, close = parens
    repr_data = ', '.join(map(expr_source, data))
    return '%s%s%s' % (open, repr_data, close)


def repr_op(op):
    return op.value
