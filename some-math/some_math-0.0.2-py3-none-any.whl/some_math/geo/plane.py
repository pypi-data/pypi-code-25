# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from . import normalized

###############################################################################
def plane_plane_intersection(v1, d1, v2, d2):
    n1 = normalized(v1)
    a1 = d1 / np.linalg.norm(v1)
    
    n2 = normalized(v2)
    a2 = d2 / np.linalg.norm(v2)
    
    n = normalized(np.cross(n1, n2))

    cos_alpha = np.dot(n1, n2)

    q = ((a1 - a2 * cos_alpha) * n1
         + (a2 - a1 * cos_alpha) * n2) / (1 - cos_alpha**2)

    t = - np.dot(n, q)
    v = q + t * n
    
    return n, v

###############################################################################
class Plane:
    def __init__(self, n = (1, 0, 0), a = 0):
        ### normal vector
        self.n = normalized(n)
        nx, ny, nz = self.n

        ### distance from origin
        self.a = a
        
        ### angles
        self.azimut = np.arctan2(ny, nx)
        self.theta = np.arccos(nz)

    def setAzimut(self, azimut):
        self.azimut = azimut
        self.updateNormal()

    def setTheta(self, theta):
        self.theta = theta
        self.updateNormal()

    def setDistance(self, a):
        self.a = a
        
    def updateNormal(self):
        nxy = np.sin(self.theta) 
        nx =  nxy * np.cos(self.azimut)
        ny =  nxy * np.sin(self.azimut)      
        nz = np.cos(self.theta)

        self.n = np.array([nx, ny, nz])
        
    def LineSegmentCut(self, ls):
        n12 = np.dot(self.n, ls.X12)
        
        if not np.isclose(n12, 0):
            c = (self.a - np.dot(self.n, ls.X1)) / n12
        else:
            c = np.nan
        
        if (c >= 0 and c <= 1):
            Xc = ls.X1 + c * ls.X12
        else:
            Xc = None
        
        return Xc