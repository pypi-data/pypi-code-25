"""

Usage:
    exverify <testname> <configname> --cell=<cellname> [--filter=<filtername>] [--plot=<layer>] [--model=modelname] [--logging=<log>]
    exverify <testname> <configname> --cell=<cellname [--debug=<debug>]
    exverify (-h | --help)
    exverify (-v | --version)

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



from docopt import docopt
from itertools import count

import networkx as nx

import os
import sys
import yuna
import auron
import gdspy

from exverify import tools
from exverify import version
from exverify import convert

from .tools import logging

from collections import defaultdict
from networkx.algorithms import isomorphism


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


def phoenixdown():
    """
    Main function of the Auron package.
    Generates a subgraph for each wirechain
    and then combines them into one graph network.
    """

    args = docopt(__doc__, version=version.__version__)
    tools.cyan_print('Summoning ExVerify...')
    tools.parameter_print(args)

    tools.args = args

    if args['--logging'] == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif args['--logging'] == 'info':
        logging.basicConfig(level=logging.INFO)

    if _cell_accepted(args):
        g1 = auron.bushido(args)

        if g1 is None:
            tools.green_print('No graph was generated')
        else:
            convert.to_netlist(g1, args['<testname>'])
            g2 = convert.to_graph(args['<testname>'])

            GM = isomorphism.GraphMatcher(g1, g2)
            if GM.is_isomorphic():
                print('\nYES - LN and SN matches :)\n')
            else:
                print('\nNO - LN & SN does not match :(\n')