# Copyright 2010 by Philipp Kraft
# This file is part of cmf.
#
#   cmf is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   cmf is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with cmf.  If not, see <http://www.gnu.org/licenses/>.
#

"""
cmf.geometry deals with the geometry of cmf objects. In many cases
users do not need to care about the geometry in cmf and therefore
can ignore this package. Even in a fully distributed model, it is
not the geometry that counts, but the topology of the objects.
However, topological information can be derived from geometric structure,
and this is what this module is for.

Depends on shapely
"""

from .cmf_core import Cell
from shapely.wkb import loads as __load_wkb
from shapely.geos import WKBReadingError as WKBReadingError

def __add_geometry_property():
    """
    Extends the Cell class with a geometry attribute
    :return:
    """

    def get_geometry(c):
        try:
            return __load_wkb(c.get_WKB())
        except (TypeError, WKBReadingError):
            return None

    def set_geometry(c, geom):
        c.set_WKB(geom.wkb)

    def del_geometry(c):
        c.set_WKB(b'')

    prop = property(get_geometry, set_geometry, del_geometry, 'Geometry of the cell')
    setattr(Cell, 'geometry', prop)

def create_cell(project, polygon, height, id=None, with_surfacewater=True):
    """
    Creates a cell from a shapely polygon and stores the geometry in cell.geometry

    :param project: the cmf project of the cell
    :param polygon: the shapely Polygon
    :param height: the height of the cell
    :param id: the id of the cell, only set if not None
    :param with_surfacewater: True, if a surfacewater storage will be created
    :return: The new cell
    """

    # Get the center
    center = polygon.centroid.x, polygon.centroid.y, height
    # Create the cell
    c = project.NewCell(*center, area=polygon.area, with_surfacewater=with_surfacewater)
    # Set the geometry
    c.geometry = polygon
    # Set the id, if given.
    if id is not None:
        c.Id = id
    return c

__add_geometry_property()
