import csv
from abc import abstractmethod, ABCMeta
from collections import Mapping
from itertools import chain, repeat, islice

from six import StringIO

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives import flag, unchanged_required, unchanged
from docutils.parsers.rst.directives.images import Image
from docutils.parsers.rst.directives.tables import Table
from docutils.statemachine import StringList
from docutils.utils import SystemMessagePropagation
from sphinx.ext.autosummary import import_by_name

class NonStringIterable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is NonStringIterable:
            if any("__iter__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


def pad_infinite(iterable, padding=None):
   return chain(iterable, repeat(padding))


def pad(iterable, size, padding=None):
   return islice(pad_infinite(iterable, padding), size)


class ItemsTableDirective(Directive):
    """Format a sequence as a table.

    If the items of the sequence are themselves sequences, they will formatted as rows.
    """

    required_arguments = 1
    has_content = False
    option_spec = {
        'title': unchanged_required,
        'header-rows': directives.nonnegative_int,
        'stub-columns': directives.nonnegative_int,
        'header': unchanged,
        'transpose': flag,
        'show-row-index-with-base': int,
        'show-column-index-with-base': int,
        'stub-columns': int,
        'cell-format': unchanged_required,
        'widths': directives.value_or(
            ('auto', 'grid'),
            directives.positive_int_list)
    }

    @property
    def widths(self):
        return self.options.get('widths', '')

    @property
    def header_rows(self):
        return self.options.get('header-rows', 0)

    @property
    def stub_columns(self):
        return self.options.get('stub-columns', 0)

    def get_column_widths(self, max_cols):
        if isinstance(self.widths, list):
            if len(self.widths) != max_cols:
                raise self.error(
                    "{!s} widths do not match the number of columns {!s} in table. ({} directive)."
                        .format(self.widths, max_cols, self.name))
            col_widths = self.widths
        elif max_cols:
            col_widths = [100 // max_cols] * max_cols
        else:
            raise self.error(
                "Something went wrong calculating column widths. ({} directive).".format(self.name)
            )
        return col_widths

    def process_header_option(self):
        table_head = []
        max_header_cols = 0
        if 'header' in self.options:
            # TODO: Have the option for this to be a Python object too.
            header = self.options['header']
            header_stream = StringIO(header)
            reader = csv.reader(header_stream, delimiter=',', quotechar='"')
            header_row = next(reader)
            stripped_header_row = [cell.strip() for cell in header_row]
            table_head.append(stripped_header_row)
            max_header_cols = len(header_row)
        return table_head, max_header_cols

    @staticmethod
    def interpret_obj(obj):
        """Interpret the given Python object as a table.

        Args:
            obj: A sequence (later a mapping, too)

        Returns:
            A list of lists represents rows of cells.

        Raises:
            TypeError: If the type couldn't be interpreted as a table.
        """
        if isinstance(obj, list):
            max_cols, rows = ItemsTableDirective.interpret_list(obj)
        elif isinstance(obj, Mapping):
            max_cols, rows = ItemsTableDirective.interpret_dict(obj)
        else:
            # TODO: We can do fancy stuff like dicts of dicts later!
            raise TypeError("Unsupported Python object {!r} for tables.")

        rectangular_rows = [list(pad(row, max_cols, '')) for row in rows]

        return rectangular_rows, max_cols

    @staticmethod
    def make_row(obj_row):
        return list(obj_row) if isinstance(obj_row, NonStringIterable) else [obj_row]

    @staticmethod
    def interpret_list(obj):
        """This should handle a list items and of a list of lists of items."""
        rows = []
        max_cols = 0
        for obj_row in obj:
            row = ItemsTableDirective.make_row(obj_row)
            max_cols = max(max_cols, len(row))
            rows.append(row)
        return max_cols, rows

    @staticmethod
    def interpret_dict(obj):
        """This should handle a dictionary of items and a dictionary of lists of items."""
        rows = []
        max_cols = 0
        for key, value in obj.items():
            row = [key]
            row.extend(ItemsTableDirective.make_row(value))
            max_cols = max(max_cols, len(row))
            rows.append(row)
        return max_cols, rows

    def augment_cells(self, rows, source):
        """Convert each cell into a tuple suitable for consumption by build_table.

        I think this has to do with cell spans, but I'm not sure, and we don't need it.
        """
        # TODO: Hardwired str transform.
        return [[(0, 0, 0, StringList(str(cell).splitlines(), source=source))
                 for cell in row] for row in rows]

    def run(self):

        obj_name = self.arguments[0]

        try:
            prefixed_name, obj, parent, modname = import_by_name(obj_name)
        except ImportError:
            raise self.error(
                "Could not locate Python object {}. ({} directive).".format(obj_name, self.name))
        table_head, max_header_cols = self.process_header_option()
        rows, max_cols = self.interpret_obj(obj)
        max_cols = max(max_cols, max_header_cols)
        col_widths = self.get_column_widths(max_cols)
        table_head.extend(rows[:self.header_rows])
        table_body = rows[self.header_rows:]

        table_head = self.augment_cells(table_head, source=prefixed_name)
        table_body = self.augment_cells(table_body, source=prefixed_name)

        table = (col_widths, table_head, table_body)
        table_node = self.state.build_table(table, self.content_offset,
                                            self.stub_columns, widths=self.widths)
        table_node['classes'] += self.options.get('class', [])
        if 'align' in self.options:
            table_node['align'] = self.options.get('align')
        self.add_name(table_node)

        return [table_node]
