# -*- coding: utf-8 -*-

###############################################################################
import numpy as np
import unittest

from some_math.fit_circle import CircleFit, taubin

###############################################################################
class TestCircleFit(unittest.TestCase):
    def test_00_circleFit(self):
        radius = 10
        N = 20
        
        xc, yc = (5, 3)
        
        alpha = 2 * np.pi * np.random.rand(N)
        r = radius + 0.01 * np.random.randn(N)

        x = xc + r * np.cos(alpha)
        y = yc + r * np.sin(alpha)
        
        circleFit = CircleFit(x, y)

        xc_hat = circleFit.xc
        self.assertAlmostEqual(xc_hat, xc, delta=0.01)

        yc_hat = circleFit.yc
        self.assertAlmostEqual(yc_hat, yc, delta=0.01)

        radius_hat = circleFit.R
        self.assertAlmostEqual(radius_hat, radius, delta=0.01)
        
        residue_hat = circleFit.residue
        self.assertLess(residue_hat, 0.01)
        
    def test_01_taubin(self):
        N = 1000
        alpha_deg_0 = 265
        alpha_deg_1 = 275
        
        alpha_deg = np.linspace(alpha_deg_0, alpha_deg_1, N)
        alpha = np.radians(alpha_deg)
        
        R = 75
        xc = 3
        yc = R + 1
        
        x = R * np.cos(alpha) + xc + 0.01 * np.random.randn(N)
        y = R * np.sin(alpha) + yc + 0.01 * np.random.randn(N)
        
        xy = np.vstack((x, y)).T
        xc_hat, yc_hat, R_hat = taubin(xy)
        
        self.assertAlmostEqual(xc_hat, xc, delta=0.1)
        self.assertAlmostEqual(yc_hat, yc, delta=1)
        self.assertAlmostEqual(R_hat, R, delta=1)
