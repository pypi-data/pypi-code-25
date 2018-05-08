from added_value.all_items_role import all_items_role
from added_value.any_items_role import any_items_role
from added_value.format_role import format_role
from added_value.items_table_directive import ItemsTableDirective
from added_value.str_role import str_role
from added_value.repr_role import repr_role
from added_value.version import __version__


def setup(app):
    if not hasattr(app, 'add_config_value'):
        return  # probably called by nose, better bail out

    app.add_role('repr', repr_role)
    app.add_role('str', str_role)
    app.add_role('format', format_role)
    app.add_role('any-items', all_items_role)
    app.add_role('any-items', any_items_role)
    app.add_directive('items-table', ItemsTableDirective)

    return {'version': __version__}