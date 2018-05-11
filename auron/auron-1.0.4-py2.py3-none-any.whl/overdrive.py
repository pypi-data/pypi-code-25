"""

Usage:
    auron <testname> <configname> --cell=<cellname> [--filter=<filtername>] [--plot=<layer>] [--model=modelname] [--logging=<log>]
    auron <testname> <configname> --cell=<cellname [--debug=<debug>]
    auron (-h | --help)
    auron (-v | --version)

Option:
    -h --help            show this screen.
    -v --version         show version.
    --verbose            print more text

    <testname>         - GDS file name
    <configname>       - Process Data File name (.json)

    --cell=cellname    - Cell name to be extracted
           list        - List the cells in the .gds file

    --filter=setup     - init the first filtering step
             usernodes - detect & add usernodes
             wires     - refilter netwwork after adding usernodes
             series    - remove the series connected edges.

    --plot=layer       - Only for debugging. Plot the LVS graphs

    --model=modelname  - Generate a 3D circuit model from the .gds file.

"""


import sys

from docopt import docopt
from itertools import count
from auron import version

from auron import filters
from auron import tools
from auron import netlist
import networkx as nx

import yuna
import os
import gdspy
import meshio

from auron import mesh
from auron import graph

from yuna import masternodes as mn
from auron import edge_labels as el
from .tools import logging

from collections import defaultdict


"""

Hacker: 1h3d*n
For: Volundr
Docs: Algorithm 1
Date: 31 April 2017

Description: Morph the moat layer and the wire layers.

1) Get a list of all the polygons inside the GDS file.
2) Send this list to the Clip library with the wiring
   layer number and the moat layer number as parameters.
3) Get the union of all the wiring layer polygons that
   are connected. Update this to check for vias.
4) Get the intersection of the moat layer with the
   wiring layer and save this in a new polygon.
5) Get the difference of the moat layer with the
   wiring layer and save this in a new polygon.
6) Join the intersected and difference polygons
   to form a list of atleast 3 polygons.
7) We now know which part of the wiring layer
   goes over the moat is most probably mutually
   connected to wiring layer 2.
8) Send this polygon structure to GMSH.

"""


def _cell_accepted(args):
    gds_file = os.getcwd() + '/' + args['<testname>'] + '.gds'
    gdsii = gdspy.GdsLibrary()
    gdsii.read_gds(gds_file, unit=1.0e-12)

    accept = True

    if args['--cell'] == 'ntrons':
        tools.list_ntron_cells(gdsii)
        accept = False
    elif args['--cell'] == 'jjs':
        tools.list_jj_cells(gdsii)
        accept = False
    elif args['--cell'] == 'vias':
        tools.list_via_cells(gdsii)
        accept = False
    elif args['--cell'] == 'list':
        tools.list_layout_cells(gdsii)
        accept = False
    else:
        if args['--cell'] not in gdsii.cell_dict.keys():
            raise ValueError('not a valid cell name')

    return accept


def _combine_mask_graphs(args, wirechain):
    """
    Combine the different subgraphs for each
    wirechain. The wirechain is the list of
    polygons that represents on layer type.

    Parameters
    ----------
    wirechain : dist()
        key is the layer name and value is the
        subgraph of that layer network
    Params : dict()
        Node id in the graph

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    tools.green_print('Combining subgraphs...')

    graphs = [sg for sg in wirechain.values()]
    g = nx.disjoint_union_all(graphs)
    g = filters.combine_nodes(g)

    return g


def _device_labels(g):
    for n in g.nodes():
        if 'label' in g.node[n]:
            if isinstance(g.node[n]['label'], mn.Ntron):
                for i in g[n]:
                    if g.node[i]['poly'].id == g.node[n]['poly'].id:
                        g.node[i]['device'] = g.node[n]['label']
                        g.node[n]['device'] = g.node[n]['label']

    return filters.combine_nodes(g)


def bushido(args):
    """
    Main function of the Auron package.
    Generates a subgraph for each wirechain
    and then combines them into one graph network.
    """

    # args = docopt(__doc__, version=version.__version__)
    tools.cyan_print('Summoning Auron...')
    tools.parameter_print(args)

    tools.args = args

    if args['--logging'] == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif args['--logging'] == 'info':
        logging.basicConfig(level=logging.INFO)

    if _cell_accepted(args):
        datafield = yuna.grand_summon(os.getcwd(), args)

        if datafield is None:
            raise ValueError('datafield cannot be None')

        if args['--debug'] == 'polygons':
            mesh.mask_network(args, datafield)
        else:
            networks = mesh.mask_network(args, datafield)

            tools.green_print('Proceeding to merge subgraphs')

            if len(networks) > 1:
                g = _combine_mask_graphs(args, networks)
                g = _device_labels(g)
                g = filters.subgraphs(g)
            else:
                g = list(networks.values())[0]

            if args['--filter'] == 'series':
                tools.magenta_print('Filtering phase')

                g = filters.series_nodes(g)
                g = filters.noise_nodes(g, 0)
                g = filters.series_nodes(g)

            g = el.inductor_edges(g)
            g = el.capacitor_edges(g)

            tools.plot_network(networks, g, args)
            tools.cyan_print('Auron. Done.\n')

            return g

    return None
