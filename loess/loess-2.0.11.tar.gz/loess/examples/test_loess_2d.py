#!/usr/bin/env python
##############################################################################
#
# Usage example for the procedure loess_2d
#
# MODIFICATION HISTORY:
#   V1.0.0: Written by Michele Cappellari, Oxford 26 February 2014
#   V1.0.1: Changed imports for loess and plotbin as packages. 
#       Removed overlap of axes labels. MC, Oxford, 17 April 2018    
#
##############################################################################

import numpy as np
import matplotlib.pyplot as plt

from time import clock

from loess.loess_2d import loess_2d
from plotbin.plot_velfield import plot_velfield

def test_loess_2d():
    """
    Usage example for loess_2d

    """
    n = 200
    x = np.random.uniform(-1,1,n)
    y = np.random.uniform(-1,1,n)
    z = x**2 - y**2
    sigz = 0.2
    zran = np.random.normal(z, sigz)

    t = clock()
    zout, wout = loess_2d(x, y, zran)
    print(clock() - t)

    plt.clf()
    plt.subplot(131)
    plot_velfield(x, y, z)
    plt.title("True Function")

    plt.subplot(132)
    plot_velfield(x, y, zran)
    plt.title("With Noise Added")
    plt.tick_params(labelleft=False)

    plt.subplot(133)
    plot_velfield(x, y, zout)
    plt.title("LOESS Recovery")
    plt.tick_params(labelleft=False)
    plt.pause(1)

#------------------------------------------------------------------------

if __name__ == '__main__':
    test_loess_2d()
