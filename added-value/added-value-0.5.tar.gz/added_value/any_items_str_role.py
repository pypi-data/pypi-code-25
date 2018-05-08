from docutils import nodes

from added_value.pyobj_role import make_pyobj_role


def make_any_items_str_node(rawtext, app, prefixed_name, obj, parent, modname, options):
    """Render a Python sequence as a comma-separated list, with an "and" for the final item.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param prefixed_name: The dotted Python name for obj.
    :param obj: The Python object to be rendered to text.
    :param parent: The parent Python object of obj.
    :param module: The name of the module containing obj.
    :param options: Options dictionary passed to role func.
    """
    if len(obj) == 0:
        text = ''
    elif len(obj) == 1:
        text = str(obj)
    elif len(obj) == 2:
        text = "{!s} and {!s}".format(obj[0], obj[1])
    else:
        all_but_last = ', '.join(map(str, obj[:-1]))
        last = obj[-1]
        text = "{}, or {!s}".format(all_but_last, last)
    node = nodes.Text(text, rawsource=rawtext)
    return node

any_items_str_role = make_pyobj_role(make_any_items_str_node)
