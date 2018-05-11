from auron import tools
import pyclipper
import networkx as nx

from yuna import process
from auron import compress
from .tools import logging

from yuna import masternodes as mn
from collections import defaultdict

logger = logging.getLogger(__name__)


def _triangle_polygon(tri, pp):
    n1, n2, n3 = pp[tri[0]], pp[tri[1]], pp[tri[2]]

    n1 = tools.convert_node_to_2d(n1)
    n2 = tools.convert_node_to_2d(n2)
    n3 = tools.convert_node_to_2d(n3)

    return [n1, n2, n3]


def terminals(g, gds, mesh, datafield):
    logger.info('Adding terminals')

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        for label in datafield.labels:
            if isinstance(label, mn.Terminal):
                if gds in label.data.metals:
                    if tools._point_inside(points, label.position):
                        # print('    .' + label.text)

                        g.node[n]['label'] = label
    
    return g


def vias(g, gds, mesh, datafield):
    logger.info('Adding vias')

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        for label in datafield.labels:
            if isinstance(label, mn.Via):
                if gds in label.data['metals']:
                    if tools._point_inside(points, label.position):
                        # print('    .' + label.text)

                        g.node[n]['label'] = label
    
    return g


def capacitance(g, gds, mesh, datafield):
    logger.info('Adding capacitances')

    # edges = defaultdict(list)

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        for lbl in datafield.labels:
            if isinstance(lbl, mn.Capacitor):
                if gds in lbl.data.metals:
                    if tools._point_inside(points, lbl.position):
                        # print('    .' + lbl.text + ' (' + str(gds) + ')')

                        lid = '{}_{}_{}'.format(lbl.id, 
                                               lbl.plates[gds].term,
                                               lbl.plates[gds].label)

                        cap = mn.Capacitor(datafield.pcd.layers['cap'], 
                                           lbl.plates[gds].label,
                                           lbl.position, 
                                           lbl.layer,
                                           id0=lid)

                        # name = lbl.text.split(' ')[0]
                        # if name in edges:
                        #     edges[name].append(n)
                        # else:
                        #     edges[name] = [n]

                        g.node[n]['label'] = cap

    # for key, edge in edges.items():
    #     if key[0] == 'C':
    #         e = tuple(edge)
    #         g.add_edge(*e, label='None')
    
    return g


def junctions(g, gds, mesh, datafield):
    logger.info('Adding junctions')

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        surface_id = None

        for label in datafield.labels:
            if isinstance(label, mn.Junction):
                if gds in label.data['metals']:
                    if tools._point_inside(points, label.position):
                        # print('    .' + label.text)

                        g.node[n]['label'] = label
                        surface_id = g.node[n]['poly'].id

                        for m in g.nodes():
                            if g.node[m]['poly'].id == surface_id:
                                if 'label' not in g.node[m]:
                                    g.node[m]['label'] = label
    
    return g


def shunt(g, gds, mesh, datafield):
    logger.info('Adding shunt')

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        for label in datafield.labels:
            if isinstance(label, mn.Shunt):
                if gds in label.data['metals']:
                    if tools._point_inside(points, label.position):
                        # print('    .' + label.text)

                        g.node[n]['label'] = label
    
    return g


def ground(g, gds, mesh, datafield):
    logger.info('Adding ground')

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        for label in datafield.labels:
            if isinstance(label, mn.Ground):
                if gds in label.data['metals']:
                    if tools._point_inside(points, label.position):
                        # print('    .' + label.text)

                        g.node[n]['label'] = label

    return g


def ntrons(g, gds, mesh, datafield):
    logger.info('Adding ntrons')

    for n, tri in enumerate(mesh['cells']['triangle']):
        points = _triangle_polygon(tri, mesh['points'])

        for label in datafield.labels:
            if isinstance(label, mn.Ntron):
                if gds in label.data['metals']:
                    if tools._point_inside(points, label.position):
                        # print('    .' + label.text)

                        g.node[n]['label'] = label
    
    return g




