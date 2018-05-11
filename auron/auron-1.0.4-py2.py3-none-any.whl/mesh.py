import os
import meshio
import pygmsh
import pyclipper

import networkx as nx
import numpy as np

from auron import filters
from auron import tools
from auron import graph
from auron import compress
import types

from .tools import logging

from auron import pin_labels as pl
from auron import surface_labels as sl


logger = logging.getLogger(__name__)


# def log_newline(self, how_many_lines=1):
#     self.handler.setFormatter(self.blank_formatter)
#     for i in range(how_many_lines):
#         self.info('')
#     self.handler.setFormatter(self.formatter)


# def create_logger():
#     handler = logging.StreamHandler()
#     handler.setLevel(logging.DEBUG)
#     formatter = logging.Formatter(fmt="%(name)s %(levelname)-8s: %(message)s")        
#     blank_formatter = logging.Formatter(fmt="")
#     handler.setFormatter(formatter)

#     # Create a logger, with the previously-defined handler
#     logger = logging.getLogger('logging_test')
#     logger.setLevel(logging.DEBUG)
#     logger.addHandler(handler)

#     # Save some data and add a method to logger object
#     logger.handler = handler
#     logger.formatter = formatter
#     logger.blank_formatter = blank_formatter
#     logger.newline = types.MethodType(log_newline, logger)

#     return logger


def _update_mask(geom, poly_list, mask, datafield):
    """

    """

    # logger = create_logger()
    # logger.newline()

    logger.info('Updating mask')

    for i, poly in enumerate(poly_list):
        pp = poly.get_points(0)

        polyname = str(poly.layer) + '_' + str(poly.datatype) + '_' + str(i)

        gp = geom.add_polygon(pp, lcar=1.0, make_surface=True)
        geom.add_physical_surface(gp.surface, label=polyname)

        if poly.layer in mask:
            mask[poly.layer].append(gp.surface)
        else:
            mask[poly.layer] = [gp.surface]


def _generate_mesh(gds, geom):
    """

    """

    tools.green_print('Meshing layer - ' + str(gds))

    geom.add_raw_code('Mesh.Algorithm = 100;')

    meshdata = pygmsh.generate_mesh(geom, 
                                    verbose=False, 
                                    prune_vertices=False, 
                                    geo_filename=str(gds) + '.geo')

    meshfields = dict()

    meshfields['points'] = meshdata[0]
    meshfields['cells'] = meshdata[1]
    meshfields['point_data'] = meshdata[2]
    meshfields['cell_data'] = meshdata[3]
    meshfields['field_data'] = meshdata[4]

    # assert isinstance(meshfields['points'], np.ndarray)
    # assert isinstance(meshfields['cells']['triangle'], np.ndarray)
    # assert isinstance(meshfields['point_data'], np.ndarray)
    # assert isinstance(meshfields['cell_data'], np.ndarray)
    # assert isinstance(meshfields['field_data'], np.ndarray)

    directory = os.getcwd() + '/mesh/'
    mesh_file = directory + str(gds) + '.msh'
    vtk_file = directory + str(gds) + '.vtk'

    if not os.path.exists(directory):
        os.makedirs(directory)

    meshio.write(mesh_file, *meshdata)
    # meshio.write(vtk_file, *meshdata)

    return meshfields


def _add_surface_labels(g, meshfields, datafield):
    tools.green_print('Adding surface_labels')

    g = sl.inductors(g, meshfields, datafield)
    g = sl.vias(g, meshfields, datafield)
    g = sl.junctions(g, meshfields, datafield)
    g = sl.ntrons(g, meshfields, datafield)

    return g


def _add_pin_labels(g, gds, meshfields, datafield):
    tools.green_print('Adding pin_labels')

    g = pl.terminals(g, gds, meshfields, datafield)
    g = pl.vias(g, gds, meshfields, datafield)
    g = pl.capacitance(g, gds, meshfields, datafield)
    g = pl.junctions(g, gds, meshfields, datafield)
    g = pl.shunt(g, gds, meshfields, datafield)
    g = pl.ground(g, gds, meshfields, datafield)
    g = pl.ntrons(g, gds, meshfields, datafield)

    return g


def mask_network(args, datafield):
    networks = dict()

    tools.magenta_print('Generating subgraph for layer')

    wires = {**datafield.pcd.layers['ix'],
             **datafield.pcd.layers['term'],
             **datafield.pcd.layers['ntron'],
             **datafield.pcd.layers['res']}

    for gds in wires.keys():
        geom = pygmsh.opencascade.Geometry()

        geom.add_raw_code('Mesh.CharacteristicLengthMin = 1;')
        geom.add_raw_code('Mesh.CharacteristicLengthMax = 1;')

        mask_geo = dict()
        for datatype, poly_list in datafield.polygons[gds].items():
            key = (gds, datatype)
            _update_mask(geom, poly_list, mask_geo, datafield)

        for key, surfaces in mask_geo.items():
            if len(surfaces) > 1:
                union = geom.boolean_union(surfaces)
            # else:
            #     union = geom.boolean_union([surfaces])

            meshfields = _generate_mesh(gds, geom)

            logger.info('Graph geometry')

            g = nx.Graph()

            g = graph.create_graph_edges(g, meshfields)
            g = graph.position_graph_nodes(g, meshfields)

            logger.info('Graph labels')

            g = _add_surface_labels(g, meshfields, datafield)
            g = _add_pin_labels(g, gds, meshfields, datafield)

            # g = filters.get_quotient_nodes(g)

            # g = compress.vias(g)
            # g = compress.junctions(g)
            # g = compress.layers(g)

            networks[gds] = g

    return networks
