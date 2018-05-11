import os
import sys
import plotly
import pyclipper
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from yuna import masternodes as mn
from auron import edge_labels as el

from termcolor import colored
from collections import defaultdict
from plotly.graph_objs import *

import logging


args = None


def _point_inside(points, position):
    assert position is not None, 'No label position found.'
    if pyclipper.PointInPolygon(position, points) != 0:
        return True
    return False


def plot_network(layergraphs, g,  args):
    if args['--plot'] == 'all':
        draw_plotly(g, 'netlist_graph')
    elif args['--plot'] == 'layers':
        for gds, lg in layergraphs.items():
            draw_plotly(lg, str(gds))


def draw_plotly(G, layername):
    edge_trace = Scatter(
        x=[],
        y=[],
        line=Line(width=1.5, color='#888'),
        hoverinfo='none',
        mode='line')

    edge_label_trace = Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=Marker(
            color='#6666FF',
            size=2,
            line=dict(width=4)))

    for e in G.edges():
        x0, y0 = G.node[e[0]]['pos']
        x1, y1 = G.node[e[1]]['pos']

        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]

        x = x0 + (x1-x0)/2.0
        y = y0 + (y1-y0)/2.0

        edge_label_trace['x'].append(x)
        edge_label_trace['y'].append(y)

        edge = G[e[0]][e[1]]

        if 'label' in edge:
            if isinstance(edge['label'], el.Capacitor):
                edge_label_trace['text'].append(edge['label'].id)
            if isinstance(edge['label'], el.Inductor):
                edge_label_trace['text'].append(edge['label'].id)

    node_trace = Scatter(
        x=[],
        y=[],
        text=[],
        name='markers',
        mode='markers',
        hoverinfo='text',
        marker=Marker(
            color=[],
            size=30,
            line=dict(width=2)))

    for n in G.nodes():
        x, y = G.node[n]['pos']

        node_trace['x'].append(x)
        node_trace['y'].append(y)

        if 'device' in G.node[n]:
            label = G.node[n]['device']
            # node_trace['text'].append('device_' + label.id)
        elif 'label' in G.node[n]:
            label = G.node[n]['label']
            # node_trace['text'].append('label_' + label.id)
        else:
            label = G.node[n]['poly']
            # node_trace['text'].append(label.id)

        node_trace['text'].append(label.id)

        # label = G.node[n]['poly']
        # node_trace['text'].append('id_' + str(n))

        if isinstance(label, mn.Terminal) or isinstance(label, mn.Capacitor):
            node_trace['marker']['color'].append(label.data.color)
        else:
            node_trace['marker']['color'].append(label.data['color'])

    fig = Figure(data=Data([edge_trace, node_trace, edge_label_trace]),
                layout=Layout(
                title='<br>' + layername,
                titlefont=dict(size=24),
                showlegend=False,
                width=1200,
                height=1200,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))

    plotly.offline.plot(fig, filename=layername)


def is_master(label):
    if isinstance(label, mn.Terminal):
        return True
    elif isinstance(label, mn.Capacitor):
        return True
    elif isinstance(label, mn.Via):
        return True
    elif isinstance(label, mn.Junction):
        return True
    elif isinstance(label, mn.Shunt):
        return True
    elif isinstance(label, mn.Ground):
        return True
    elif isinstance(label, mn.Ntron):
        return True
    elif isinstance(label, mn.UserNode):
        return True
    else:
        return False


def list_layout_cells(gdsii):
    """ List the Cells in the GDS layout. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Please choose a Cell from the list below:')
    for key, value in gdsii.cell_dict.items():
        print('      -> ' + key)
    print('')


def list_ntron_cells(gdsii):
    """ List the Cells in the GDS layout. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('The following nTron cells are detected:')
    for key, value in gdsii.cell_dict.items():
        if key.split('_')[0] == 'ntron':
            print('      -> ' + key)
    print('')


def list_jj_cells(gdsii):
    """ List the Cells in the GDS layout. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('The following Junction cells are detected:')
    for key, value in gdsii.cell_dict.items():
        if key.split('_')[0] == 'jj':
            print('      -> ' + key)
    print('')


def list_via_cells(gdsii):
    """ List the Cells in the GDS layout. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('The following Via cells are detected:')
    for key, value in gdsii.cell_dict.items():
        if key.split('_')[0] == 'via':
            print('      -> ' + key)
    print('')


def convert_node_to_3d(wire, z_start):
    layer = np.array(wire).tolist()

    polygons = []
    for pl in layer:
        poly = [[float(y*10e-9) for y in x] for x in pl]
        for row in poly:
            row.append(z_start)
        polygons.append(poly)
    return polygons


def convert_node_to_2d(layer):
    um = 10e7

    layer = list(layer)
    del layer[2]

    layer[0] = layer[0] * um
    layer[1] = layer[1] * um

    return layer


def parameter_print(args):
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print ('Parameters:')
    for key, value in args.items():
        print('      ' + str(key) + ' : ' + str(value))
    print('')


def red_print(header):
    """ Main program header (Red) """
    print ('\n' + '[' + colored('*', 'red', attrs=['bold']) + '] ', end='')
    print(header)


def magenta_print(header):
    """ Python package header (Purple) """
    print ('--- ' + colored(header, 'red', attrs=['bold']) + ' ', end='')
    print ('----------')


def green_print(header):
    """ Function header (Green) """
    print('')
    print ('[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print(header)


def cyan_print(header):
    """ Function header (Green) """
    print('')
    print ('[' + colored('+++', 'cyan', attrs=['bold']) + '] ', end='')
    print(header)
