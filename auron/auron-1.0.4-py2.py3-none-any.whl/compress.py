from auron import tools
import pyclipper
import networkx as nx

from yuna import process
from auron import filters

from yuna import masternodes as mn


def surface_label(g, n, mask):
    for key, nodes in mask.nodes.items():
        if n in nodes:
            for m in nodes:
                print(str(key) + ' ' + str(g.node[n]['label'].id))
                g.node[m]['color'].id = g.node[n]['label'].id
    return g


def vias(g):

    g = filters.get_quotient_nodes(g)

    # for n in g.nodes():
    #     if 'label' in g.node[n]:
    #         label = g.node[n]['label']
    #         if isinstance(label, mn.Via):
    #             g.node[n]['label'].data['color'] = "#A0A0A0"
    return g


def junctions(g):

    g = filters.get_quotient_nodes(g)

    for n in g.nodes():
        if 'label' in g.node[n]:
            label = g.node[n]['label']
            if isinstance(label, mn.Junction):
                g.node[n]['label'].data['color'] = "#FFCC99"
    return g


def layers(g):

    g = filters.get_quotient_nodes(g)

    for n in g.nodes():
        if 'label' in g.node[n]:
            label = g.node[n]['label']
            if isinstance(label, mn.Inductor):
                g.node[n]['label'].data['color'] = "#66FFB2"
    return g
