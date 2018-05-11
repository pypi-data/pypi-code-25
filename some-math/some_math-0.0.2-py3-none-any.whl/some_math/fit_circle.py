# -*- coding: utf-8 -*-
"""
Created on Thu Jun 04 07:57:15 2015

@author: twagner
"""

### imports ###################################################################
import numpy as np
import scipy.optimize

###############################################################################
def taubin(XY):
    '''Algebraic circle fit by Taubin
       G. Taubin, "Estimation Of Planar Curves, Surfaces And Nonplanar
                  Space Curves Defined By Implicit Equations, With 
                  Applications To Edge And Range Image Segmentation",
       IEEE Trans. PAMI, Vol. 13, pages 1115-1138, (1991)
    '''
    
    centroid = np.mean(XY, axis = 0) # the centroid of the data set

    X = XY[:,0] - centroid[0] #  centering data
    Y = XY[:,1] - centroid[1] #  centering data
    Z = X**2 + Y**2
    Zmean = np.mean(Z)
    Z0 = (Z - Zmean) / (2* np.sqrt(Zmean))
    ZXY = np.vstack((Z0, X, Y)).T
    
    U, S, Vt = np.linalg.svd(ZXY,0)
    V = Vt.T
    
    A = V[:,2]
    A[0] = A[0] / (2 * np.sqrt(Zmean))
    A = np.append(A, -Zmean * A[0])

    Par = np.zeros(3)
    Par[0:2] = -A[1:3] /A[0] / 2 + centroid
    Par[2] = np.sqrt(A[1]*A[1] + A[2]*A[2] - 4 * A[0] * A[3]) / abs(A[0]) / 2
        
    return Par

###############################################################################
class CircleFit:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.optimize()

    def optimize(self):
        
        x_m = np.mean(self.x)
        y_m = np.mean(self.y)

        center_estimate = x_m, y_m
        
        center, ier = scipy.optimize.leastsq(
                self.f,
                center_estimate,
                Dfun=self.Df,
                col_deriv = True)
        
        self.xc, self.yc = center
        Ri = self.calcRadius(*center)
        self.R = Ri.mean()
        self.residue = sum((Ri - self.R)**2)

    ###########################################################################
    def calcRadius(self, xc, yc):
        """ calculate the distance of each data points from the
            center (xc, yc)
        """
        return np.sqrt((self.x - xc)**2 + (self.y - yc)**2)

    def f(self, c):
        """ calculate the algebraic distance between the 2D points and the mean
            circle centered at c=(xc, yc)
        """
        
        Ri = self.calcRadius(*c)
        return Ri - Ri.mean()

    def Df(self, c):
        """ Jacobian of f_2b
            The axis corresponding to derivatives must be coherent with the
            col_deriv option of leastsq
        """
        
        xc, yc = c
        Nx = self.x.size
        
        df2b_dc    = np.empty((len(c), Nx))
    
        Ri = self.calcRadius(xc, yc)
        df2b_dc[0] = (xc - self.x) / Ri                   # dR/dxc
        df2b_dc[1] = (yc - self.y) / Ri                   # dR/dyc
        df2b_dc    = df2b_dc - df2b_dc.mean(axis = 1)[:, np.newaxis]
    
        return df2b_dc
