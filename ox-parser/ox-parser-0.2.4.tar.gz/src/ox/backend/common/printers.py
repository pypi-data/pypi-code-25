import operator


def context(expr_emitter, stm_emitter, indentation=0):
    pass


def emit(node, file, ctx):
    """
    A emiter function receives a node and a language-sensitive context
    and emits code writing using the file object and the given context.

    Args:
        node:
        context:

    Returns:
    """


def infix_operator_node(op, paren=True):
    """
    Returns an emiter for the given infix operator.
    """

    def emit(node, file, ctx):
        lhs, rhs = node.value
        if paren:
            file.write('(')
        ctx.emit_expr(lhs, file, ctx)
        file.write(op)
        ctx.emit_expr(lhs, file, ctx)
        if paren:
            file.write(')')

    return emit


def block(node, file, ctx, statements=operator.attrgetter('value'),
          open=None, close=None):
    """
    Emits code for an AST node that represents a list of statements.

    Args:
        node:
            The ast node representing the block.
        file:
            The file object used to emit code.
        ctx:
            Emission context.
        statements:
            A function that receives a node and return a list of statements.
            The default behavior is to fetch the list from the .value attribute
            of the node.
        open, close:
            The open/close tokens for the block. (e.g., "{", "}" for C-family
            languages).
    """
    write = file.write

    if open:
        write(open)
    write(ctx.new_line)

    ctx.indent += 1
    for stm in statements(node):
        ctx.emit_stm(stm, file, ctx)
        write(ctx.new_line)
    ctx.indent -= 1

    if close:
        write(close)
    write(ctx.new_line)


def fcall(node, file, ctx, open='(', close=')', sep=', '):
    """
    C-style function call from a node that has (func_name, args) elements.

    Can control the opening/closing bracket and argument separator.
    """

    func_name, args = node.value
    file.write(func_name)
    array(args, file, ctx, items=lambda x: x, open=open, close=close, sep=sep)


def array(node, file, ctx, items=operator.attrgetter('value'),
          open='{', close='}', sep=', '):
    """
    C-style array declaration. You can control the the opening/closing bracket
    and item separator and adapt it to other languages and linear data
    structures.
    """

    write = file.write
    emit = ctx.emit_expr

    data = items(node)
    write(open)

    if len(data) == 1:
        item, = data
        emit(item)
    elif len(data) > 1:
        for item in items[:-1]:
            emit(item)
            write(sep)
        emit(items[-1])
    write(close)


def assign(node, file, ctx, operator=' = ', end=';'):
    """
    Emits a C-style assignment command from a node that has a (lhs, rhs) in
    its .value attribute.

    Can control the assignment operator (=) and the line end (;).
    """

    lhs, rhs = node.value
    if isinstance(lhs, str):
        file.write(lhs)
    else:
        ctx.emit_expr(lhs)

    file.write(operator)
    ctx.emit_expr(rhs)

    if end:
        file.write(end)
