# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from some_math.geo import normalized
from some_math.geo.points_3D import Points3D

###############################################################################
class TestPoints3D(unittest.TestCase):
    def test_00_find_points(self):
        M, N = shape = (40, 20)
        flat_shape = (M * N, 3)
        
        a = 3 # distance from origin
        below = 2
        above = 4

        xmin, xmax = (0, 10)
        ymin, ymax = (0, 20)
        
        x = np.linspace(xmin, xmax, M, endpoint=False)
        y = np.linspace(ymin, ymax, N, endpoint=False)

        X, Y = np.meshgrid(x, y, indexing='ij')
        Z = a * np.ones(shape)
        P = Points3D((X, Y, Z))
        
        shape_hat = P.findPointsInAxisRange((below, above), axis=2).XYZ.shape
        self.assertEqual(shape_hat, flat_shape)

        shape_hat = P.findPointsInAxisRange((-2, 2), axis=2).XYZ.shape
        self.assertEqual(shape_hat, (0, 3))
