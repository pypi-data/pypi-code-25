#!/usr/bin/env python

"""
Tests for testing a UGrid file read.

We really need a **lot** more sample data files...

"""

from __future__ import (absolute_import, division, print_function)

import os
import pytest


import numpy as np
import netCDF4

from .utilities import chdir
from pyugrid import ugrid
from pyugrid import read_netcdf

UGrid = ugrid.UGrid

files = os.path.join(os.path.split(__file__)[0], 'files')


def test_simple_read():
    """Can it be read at all?"""
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert isinstance(grid, UGrid)


def test_get_mesh_names():
    """
    Check that it can find the mesh variable names.

    """
    with chdir(files):
        nc = netCDF4.Dataset('ElevenPoints_UGRIDv0.9.nc')
    names = read_netcdf.find_mesh_names(nc)
    assert names == [u'Mesh2']


def test_mesh_not_there():
    """Test raising Value error with incorrect mesh name."""
    with pytest.raises(ValueError):
        with chdir(files):
            UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc', mesh_name='garbage')


def test_load_grid_from_nc():
    """Test reading a fairly full example file."""
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')

    assert grid.mesh_name == 'Mesh2'
    assert grid.nodes.shape == (11, 2)
    assert grid.faces.shape == (13, 3)
    assert grid.face_face_connectivity.shape == (13, 3)
    assert grid.boundaries.shape == (9, 2)
    assert grid.edges is None


def test_read_nodes():
    """Do we get the right nodes array?"""
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.nodes.shape == (11, 2)

    # Not ideal to pull specific values out, but how else to test?
    assert np.array_equal(grid.nodes[0, :], (-62.242, 12.774999))
    assert np.array_equal(grid.nodes[-1, :], (-34.911235, 29.29379))


def test_read_none_edges():
    """Do we get the right edge array?"""

    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.edges is None


def test_read_faces():
    """Do we get the right faces array?"""

    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.faces.shape == (13, 3)

    # Not ideal to pull specific values out, but how else to test?
    assert np.array_equal(grid.faces[0, :], (2, 3, 10))
    assert np.array_equal(grid.faces[-1, :], (10, 5, 6))


def test_read_face_face():
    """Do we get the right face_face_connectivity array?"""

    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.face_face_connectivity.shape == (13, 3)

    # Not ideal to pull specific values out, but how else to test?
    assert np.array_equal(grid.face_face_connectivity[0, :], (11, 5, -1))
    assert np.array_equal(grid.face_face_connectivity[-1, :], (-1, 5, 11))


def test_read_boundaries():
    """Do we get the right boundaries array?"""

    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.boundaries.shape == (9, 2)

    # Not ideal to pull specific values out, but how else to test?
    # Note: file is 1-indexed, so these values are adjusted.
    expected_boundaries = [[0, 1], [1, 2], [2, 3],
                           [3, 4], [4, 0], [5, 6],
                           [6, 7], [7, 8], [8, 5]]
    assert np.array_equal(grid.boundaries, expected_boundaries)


def test_read_face_coordinates():
    """Do we get the right face_coordinates array?"""

    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.face_coordinates.shape == (13, 2)

    # Not ideal to pull specific values out, but how else to test?
    assert np.array_equal(grid.face_coordinates[0],
                          (-37.1904106666667, 30.57093))
    assert np.array_equal(grid.face_coordinates[-1],
                          (-38.684412, 27.7132626666667))


def test_read_none_edge_coordinates():
    """Do we get the right edge_coordinates array?"""
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.edge_coordinates is None


def test_read_none_boundary_coordinates():
    """Do we get the right boundary_coordinates array?"""
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc')
    assert grid.boundary_coordinates is None


def test_read_longitude_no_standard_name():
    with chdir(files):
        grid = UGrid.from_ncfile('no_stand_name_long.nc')
    assert grid.nodes.shape == (11, 2)

    # Not ideal to pull specific values out, but how else to test?
    assert np.array_equal(grid.nodes[0, :], (-62.242, 12.774999))
    assert np.array_equal(grid.nodes[-1, :], (-34.911235, 29.29379))


def test_read_data_keys():
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc', load_data=True)
    assert sorted(grid.data.keys()) == [u'boundary_count',
                                        u'boundary_types',
                                        u'depth']


def test_read_data():
    expected_depth = [1, 1, 1, 102, 1, 1, 60, 1, 1, 97, 1]
    expected_depth_attributes = {'standard_name': 'sea_floor_depth_below_geoid',
                                 'units': 'm',
                                 'positive': 'down',
                                 }
    with chdir(files):
        grid = UGrid.from_ncfile('ElevenPoints_UGRIDv0.9.nc', load_data=True)
    assert np.array_equal(grid.data['depth'].data, expected_depth)
    assert grid.data['depth'].attributes == expected_depth_attributes


def test_read_from_nc_dataset():
    """
    Minimal test, but makes sure you can read from an already
    open netCDF4.Dataset.

    """
    with chdir(files):
        with netCDF4.Dataset('ElevenPoints_UGRIDv0.9.nc') as nc:
            grid = UGrid.from_nc_dataset(nc)
    assert grid.mesh_name == 'Mesh2'
    assert grid.nodes.shape == (11, 2)
    assert grid.faces.shape == (13, 3)

if __name__ == "__main__":
    test_simple_read()
