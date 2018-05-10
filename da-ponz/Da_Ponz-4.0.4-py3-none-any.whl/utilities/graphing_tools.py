import da_ponz.strategies.common_functions as common_functions
import bokeh.io as bok_io
import bokeh.palettes as bok_pal
import bokeh.plotting as bok_plo
import numpy
import re


def create_graph_object(data, title):
    graph = bok_plo.figure(plot_width=950, title=title)
    line_width = 2
    palette = bok_pal.plasma(data.shape[1])
    source = bok_plo.ColumnDataSource.from_df(data)

    for i in xrange(len(palette)):
        legend = data.columns.values[i].capitalize()
        graph.line(color=palette[i], legend=legend, line_width=line_width, source=source, x='index', y=data.columns[i])

    return graph


def display_graph(file_name, graph):
    bok_io.output_file(file_name)
    bok_io.show(graph)


def graph_results(data, name):
    graph_data = prepare_graph_data(data)
    graph = create_graph_object(graph_data, ' '.join(re.split('_', name)))
    display_graph(name + '.html', graph)


def prepare_graph_data(data, headers=('train', 'test')):
    df_dict = {}

    for i in xrange(len(data)):
        if type(data[i]) is numpy.ndarray:
            line_data = data[i].flatten()

        else:
            line_data = data[i]

        df_dict[headers[i]] = line_data

    graph_data = common_functions.create_dataframe(df_dict.keys(), numpy.column_stack(df_dict.values()))

    return graph_data