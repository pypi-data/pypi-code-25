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

try:

    from shapely.wkb import loads as __load_wkb
    from shapely.geos import WKBReadingError as WKBReadingError

except ImportError:

    raise ImportError('cmf.geometry is only available if shapely is installed')


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


__add_geometry_property()


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

class __simple_quad_tree:
    """
    A simple quad tree to check if the boundaries of geometries overlap or not
    """

    def add_object(self,object,bounds):
        imin=int(bounds[0]/self.dx)
        jmin=int(bounds[1]/self.dy)
        imax=int(bounds[2]/self.dx)+1
        jmax=int(bounds[3]/self.dy)+1
        for i in range(imin,imax):
            for j in range(jmin,jmax):
                self.areas.setdefault((i,j),set()).add(object)

    def get_objects(self,bounds):
        imin=int(bounds[0]/self.dx)
        jmin=int(bounds[1]/self.dy)
        imax=int(bounds[2]/self.dx)+1
        jmax=int(bounds[3]/self.dy)+1
        res=set()
        for i in range(imin,imax):
            for j in range(jmin,jmax):
                res.update(self.areas.get((i,j),set()))
        return res

    def __init__(self,dx=20,dy=20):
        self.dx=dx
        self.dy=dy
        self.areas={}


def mesh_project(project, verbose=False):
    """
    Get the topologcial information from the geometry
    This may take some time
    :param project: The cmf project. The cells of the project need to have geometry
    :param verbose: Set True for report of action
    :return:
    """
    # Create quad tree
    q_tree = __simple_quad_tree()
    for c in project:
        if c.geometry:
            q_tree.add_object(c, c.geometry.bounds)

    if verbose:
        print("No. of connected cells:")
    report_at = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000]
    start = time.clock()
    con_count = 0
    cmp_count = 0
    for i, c in enumerate(project):
        s = c.geometry
        if verbose and i in report_at:
            print(i, end='\r')
        candidates = q_tree.get_objects(s.bounds)
        cmp_count += len(candidates)
        for ic in candidates:
            c = features[ic]
            if not s is c and pred(s, c):
                shp_s = shape_callable(s)
                shp_cmp = shape_callable(c)
                intersect = shp_s.intersection(shp_cmp).length
                if intersect:
                    cell_dict[i].topology.AddNeighbor(
                        cell_dict[ic], intersect)
                    con_count += 1
    if verbose:
        print(len(features), ' %0.2f sec. %i comparisons' %
              (time.clock() - start, cmp_count))

