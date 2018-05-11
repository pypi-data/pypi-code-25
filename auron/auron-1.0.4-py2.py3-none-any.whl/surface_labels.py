from auron import tools
import pyclipper
import networkx as nx

from yuna import process
from auron import compress
from .tools import logging

from yuna import masternodes as mn
from auron import pin_labels as pl

logger = logging.getLogger(__name__)


def inductors(g, mesh, datafield):
    """
    The layertype is found by the surface label of the meshed triangle.
    Every triangle is connected to a layer type in the layout. Each graph
    vertex represent a triangle, thus we have to map the triangle layer
    properties to the specific graph vertex.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    for n in g.nodes():
        cell_list = mesh['cell_data']['triangle']['gmsh:physical']
        layerid = cell_list.tolist()[n]

        for key, value in mesh['field_data'].items():
            if layerid in value:
                gds = int(key.split('_')[0])
                datatype = int(key.split('_')[1])

                polygons = datafield.polygons[gds][datatype]
                layername = polygons[0].data.name

                for poly in polygons:
                    if tools._point_inside(poly.points, g.node[n]['pos']):
                        g.node[n]['poly'] = mn.Inductor(poly.data.name,
                                                            poly.points,
                                                            gds,
                                                            id0=str(poly.id))
    return g


def vias(g, mesh, datafield):
    """
    The layertype is found by the surface label of the meshed triangle.
    Every triangle is connected to a layer type in the layout. Each graph
    vertex represent a triangle, thus we have to map the triangle layer
    properties to the specific graph vertex.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    logger.info('Adding vias')

    for n in g.nodes():
        cell_list = mesh['cell_data']['triangle']['gmsh:physical']
        layerid = cell_list.tolist()[n]

        for key, value in mesh['field_data'].items():
            if layerid in value:
                gds = int(key.split('_')[0])
                datatype = int(key.split('_')[1])

                polygons = datafield.polygons[gds][datatype]
                layername = polygons[0].data.name

                # if datatype == 7:
                #     print('     .ntron detected')
                #     print(polygons)
                #     print(layername)

                #     for i, poly in enumerate(polygons):
                #         print(poly.points)
                #         print(g.node[n]['pos'])

                #     print('')

                for poly in polygons:

                    # g.node[n]['poly'] = mn.Inductor(poly.data.name,
                    #                                     poly.points,
                    #                                     gds,
                    #                                     id0=str(poly.id))

                    if tools._point_inside(poly.points, g.node[n]['pos']):
                        if datatype == 1:
                            g.node[n]['poly'] = mn.Via(poly.data.name,
                                                        poly.points,
                                                        gds,
                                                        id0=str(poly.id))
    return g
    

def junctions(g, mesh, datafield):
    """
    The layertype is found by the surface label of the meshed triangle.
    Every triangle is connected to a layer type in the layout. Each graph
    vertex represent a triangle, thus we have to map the triangle layer
    properties to the specific graph vertex.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    logger.info('Adding junctions')

    for n in g.nodes():
        cell_list = mesh['cell_data']['triangle']['gmsh:physical']
        layerid = cell_list.tolist()[n]

        for key, value in mesh['field_data'].items():
            if layerid in value:
                gds = int(key.split('_')[0])
                datatype = int(key.split('_')[1])

                polygons = datafield.polygons[gds][datatype]
                layername = polygons[0].data.name

                for poly in polygons:
                    if tools._point_inside(poly.points, g.node[n]['pos']):
                        if datatype == 3:
                            g.node[n]['poly'] = mn.Junction(poly.data.name,
                                                             poly.points,
                                                             gds,
                                                             id0=str(poly.id))
    return g
    

def ntrons(g, mesh, datafield):
    """
    The layertype is found by the surface label of the meshed triangle.
    Every triangle is connected to a layer type in the layout. Each graph
    vertex represent a triangle, thus we have to map the triangle layer
    properties to the specific graph vertex.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    logger.info('Adding ntrons')

    for n in g.nodes():
        cell_list = mesh['cell_data']['triangle']['gmsh:physical']
        layerid = cell_list.tolist()[n]

        for key, value in mesh['field_data'].items():
            if layerid in value:
                gds = int(key.split('_')[0])
                datatype = int(key.split('_')[1])

                polygons = datafield.polygons[gds][datatype]
                layername = polygons[0].data.name

                for poly in polygons:
                    if tools._point_inside(poly.points, g.node[n]['pos']):
                        if datatype == 7:
                            g.node[n]['poly'] = mn.Ntron(poly.data.name,
                                                        poly.points,
                                                        gds,
                                                        id0=str(poly.id))
    return g
    