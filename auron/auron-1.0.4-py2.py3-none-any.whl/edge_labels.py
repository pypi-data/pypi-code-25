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

from yuna import masternodes as mn

from collections import defaultdict


class Capacitor(object):
    _ID = 0

    def __init__(self, id0=None):
        if id0 is None:
            self.id = 'C{}'.format(Capacitor._ID)
        else:
            self.id = id0

        Capacitor._ID += 1


class Inductor(object):
    _ID = 0

    def __init__(self, id0=None):
        if id0 is None:
            self.id = 'L{}'.format(Inductor._ID)
        else:
            self.id = id0

        Inductor._ID += 1


def inductor_edges(g):
    for e in g.edges():
        g[e[0]][e[1]]['label'] = Inductor()
    return g


def capacitor_edges(g):
    cap_edge = defaultdict()

    for n in g.nodes():
        if 'label' in g.node[n]:
            if isinstance(g.node[n]['label'], mn.Capacitor):
                _id = g.node[n]['label'].id.split('_')
                if _id[0] in cap_edge:
                    cap_edge[_id[0]].append(n)
                else:
                    cap_edge[_id[0]] = [n]

    for key, edge in cap_edge.items():
        e = tuple(edge)
        g.add_edge(*e, label=Capacitor(id0=key))

    return g

