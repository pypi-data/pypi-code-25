# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from some_math.process_capability import cp_estimation
from some_math.process_capability import cpk_estimation
from some_math.process_capability import cpm_estimation
from some_math.process_capability import cpkm_estimation

###############################################################################
class TestProcessCapabiliy(unittest.TestCase):
    def test_00_process_capability(self):
        c_limit = 6
        c_target = 1.05
        N = 2048
        target = 10
        sigma = 0.5

        mu = c_target * target
        USL = target + c_limit * sigma
        LSL = target - c_limit * sigma
        
        data = np.random.normal(loc=mu, scale=sigma, size=N)
        
        C_p = cp_estimation(data, USL, LSL)
        C_pk = cpk_estimation(data, USL, LSL)
        C_pm = cpm_estimation(data, USL, LSL, target)
        C_pkm = cpkm_estimation(data, USL, LSL, target)

        C_p_hat = (USL - LSL) / (6 * sigma)
        C_pm_hat = C_p_hat / np.sqrt(1 + (mu - target)**2 / sigma**2)

        C_pk_hat = np.min((USL - mu, mu - LSL)) / (3 * sigma)
        C_pkm_hat = C_pk_hat / np.sqrt(1 + (mu - target)**2 / sigma**2)
        
        self.assertGreaterEqual(C_p, C_pm)
        self.assertGreaterEqual(C_p, C_pk)
        self.assertGreaterEqual(C_pk, C_pkm)
        self.assertGreaterEqual(C_pm, C_pkm)
        
        self.assertAlmostEqual(C_p, C_p_hat, delta=0.1)
        self.assertAlmostEqual(C_pm, C_pm_hat, delta=0.1)

        self.assertAlmostEqual(C_pk, C_pk_hat, delta=0.1)
        self.assertAlmostEqual(C_pkm, C_pkm_hat, delta=0.1)
