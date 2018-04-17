import param

from bokeh.models.widgets import (
    DataTable, TableColumn, NumberEditor, NumberFormatter, DateFormatter,
    DateEditor, StringFormatter, StringEditor, IntEditor
)

from ...core import Dataset, Dimension
from ...element import ItemTable
from ...streams import Buffer
from ...core.util import dimension_sanitizer, datetime_types
from ..plot import GenericElementPlot
from .plot import BokehPlot
from .util import bokeh_version


class TablePlot(BokehPlot, GenericElementPlot):

    height = param.Number(default=None)

    width = param.Number(default=400)

    style_opts = (
        ['row_headers', 'selectable', 'editable', 
         'sortable', 'fit_columns', 'scroll_to_selection'] +
        (['index_position'] if bokeh_version >= '0.12.15' else [])
        )
    
    finalize_hooks = param.HookList(default=[], doc="""
        Optional list of hooks called when finalizing a column.
        The hook is passed the plot object and the displayed
        object, and other plotting handles can be accessed via plot.handles.""")

    _stream_data = True

    def __init__(self, element, plot=None, **params):
        super(TablePlot, self).__init__(element, **params)
        self.handles = {} if plot is None else self.handles['plot']
        element_ids = self.hmap.traverse(lambda x: id(x), [Dataset, ItemTable])
        self.static = len(set(element_ids)) == 1 and len(self.keys) == len(self.hmap)
        self.callbacks = self._construct_callbacks()
        self.streaming = [s for s in self.streams if isinstance(s, Buffer)]
        self.static_source = False

    def get_data(self, element, ranges, style):
        return ({dimension_sanitizer(d.name): element.dimension_values(d)
                 for d in element.dimensions()}, {}, style)


    def initialize_plot(self, ranges=None, plot=None, plots=None, source=None):
        """
        Initializes a new plot object with the last available frame.
        """
        # Get element key and ranges for frame
        element = self.hmap.last
        key = self.keys[-1]
        self.current_frame = element
        self.current_key = key

        style = self.lookup_options(element, 'style')[self.cyclic_index]
        data, _, style = self.get_data(element, ranges, style)
        if source is None:
            source = self._init_datasource(data)
        self.handles['source'] = source

        columns = self._get_columns(element, data)
        style['reorderable'] = False
        table = DataTable(source=source, columns=columns, height=self.height,
                          width=self.width, **style)
        self.handles['plot'] = table
        self.handles['glyph_renderer'] = table
        self._execute_hooks(element)
        self.drawn = True

        for cb in self.callbacks:
            cb.initialize()

        return table

    def _get_columns(self, element, data):
        columns = []
        for d in element.dimensions():
            col = dimension_sanitizer(d.name)
            kind = data[col].dtype.kind
            if kind == 'i':
                formatter = NumberFormatter()
                editor = IntEditor()
            elif kind == 'f':
                formatter = NumberFormatter(format='0,0.0[00000]')
                editor = NumberEditor()
            elif kind == 'M' or (kind == 'O' and len(data[col]) and type(data[col][0]) in datetime_types):
                dimtype = element.get_dimension_type(0)
                dformat = Dimension.type_formatters.get(dimtype, '%Y-%m-%d %H:%M:%S')
                formatter = DateFormatter(format=dformat)
                editor = DateEditor()
            else:
                formatter = StringFormatter()
                editor = StringEditor()
            column = TableColumn(field=dimension_sanitizer(d.name), title=d.pprint_label,
                                 editor=editor, formatter=formatter)
            columns.append(column)
        return columns


    def update_frame(self, key, ranges=None, plot=None):
        """
        Updates an existing plot with data corresponding
        to the key.
        """
        element = self._get_frame(key)

        # Cache frame object id to skip updating data if unchanged
        previous_id = self.handles.get('previous_id', None)
        current_id = element._plot_id
        self.handles['previous_id'] = current_id
        self.static_source = (self.dynamic and (current_id == previous_id))
        if (element is None or (not self.dynamic and self.static) or
            (self.streaming and self.streaming[0].data is self.current_frame.data
             and not self.streaming[0]._triggering) or self.static_source):
            return
        source = self.handles['source']
        style = self.lookup_options(element, 'style')[self.cyclic_index]
        data, _, style = self.get_data(element, ranges, style)
        self._update_datasource(source, data)
