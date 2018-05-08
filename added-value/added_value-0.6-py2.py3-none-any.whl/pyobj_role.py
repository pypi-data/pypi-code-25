from functools import partial

from sphinx.ext.autosummary import import_by_name

def make_pyobj_role(make_node):
    return partial(pyobj_role, make_node)

def pyobj_role(make_node, name, rawtext, text, lineno, inliner, options=None, content=None):
    """Include Python object value, rendering it to text using str.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param make_node: A callable which accepts (rawtext, app, prefixed_name, obj, parent, modname, options) and which returns a node
    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    if options is None:
        options = {}

    if content is None:
        content = []

    try:
        prefixed_name, obj, parent, modname = import_by_name(text)
    except ImportError:
        msg = inliner.reporter.error(
            "Could not locate Python object {}".format(text), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    app = inliner.document.settings.env.app
    node = make_node(rawtext, app, prefixed_name, obj, parent, modname, options)
    return [node], []

