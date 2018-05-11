# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from some_math.geo import normalized
from some_math.geo.line_segment import LineSegment
from some_math.geo.plane import plane_plane_intersection, Plane

###############################################################################
class TestPlane(unittest.TestCase):
    def test_00_intersect_with_line_segment(self):
        phi_deg = 45
        phi = np.radians(phi_deg)

        theta = np.arccos(1 / np.sqrt(3)) 
        
        p = Plane()
        p.setAzimut(phi)
        p.setTheta(theta)
        p.setDistance(3)

        C = 3 / np.sqrt(3) * np.ones(3)
        
        ls = LineSegment((0, 0, 0), (5, 5, 5))
        C_hat = p.LineSegmentCut(ls)
        
        check = np.allclose(C_hat, C)
        self.assertTrue(check)
        
    def test_01_no_intersection_with_line_segment(self):
        p = Plane(n = (0, 0, 1), a = 1)
        
        ls = LineSegment((0, 0, 0), (10, 0, 0))
        C = p.LineSegmentCut(ls)
        
        self.assertIsNone(C)
        
    def test_02_plane_plane_intersection(self):
        v1, d1 = (1, 2, 1), 1
        v2, d2 = (2, -3, 2), 2
        
        n = normalized((1, 0, -1))
        v = np.array((0.5, 0, 0.5))
        n_hat, v_hat = plane_plane_intersection(v1, d1, v2, d2)

        cos_alpha = np.dot(n_hat, v_hat)
        
        check = np.allclose(n_hat, n)
        self.assertTrue(check)
        
        check = np.allclose(v_hat, v)
        self.assertTrue(check)

        self.assertEqual(cos_alpha, 0.)