# -*- coding: utf-8 -*-

'''
    https://en.wikipedia.org/wiki/Process_capability_index
    
    LSL: lower specification limit of the process
    USL: upper specification limit of the process
    target: target process mean
'''

### imports ###################################################################
import numpy as np

###############################################################################
def cp_estimation(data, USL, LSL):
    sigma = data.std()

    cp = (USL - LSL) / 6 / sigma
    return cp

def cpm_estimation(data, USL, LSL, target):
    mu = data.mean()
    sigma = data.std()

    cp = cp_estimation(data, USL, LSL)
    root = np.sqrt(1 + ((mu - target) / sigma)**2)
    cpm = cp / root
    return cpm

def cpkm_estimation(data, USL, LSL, target):
    mu = data.mean()
    sigma = data.std()

    cpk = cpk_estimation(data, USL, LSL)
    root = np.sqrt(1 + ((mu - target) / sigma)**2)
    cpkm = cpk / root
    return cpkm

def cpk_estimation(data, USL, LSL):
    mu = data.mean()
    sigma = data.std()

    cpk = np.min((USL - mu, mu - LSL)) / 3 / sigma
    return cpk

