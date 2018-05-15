from docutils import nodes

from added_value.pyobj_role import make_pyobj_role


def make_str_node(rawtext, app, prefixed_name, obj, parent, modname, options):
    """Render a Python object to text using the repr() function.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param prefixed_name: The dotted Python name for obj.
    :param obj: The Python object to be rendered to text.
    :param parent: The parent Python object of obj.
    :param module: The name of the module containing obj.
    :param options: Options dictionary passed to role func.
    """
    text = str(obj)
    node = nodes.Text(text, rawsource=rawtext)
    return node

str_role = make_pyobj_role(make_str_node)
