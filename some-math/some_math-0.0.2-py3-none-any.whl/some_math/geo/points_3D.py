# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from ..fit_plane import fitPlane as fitPlane_XYZ
from some_math.quaternion import Quaternion

###############################################################################
class Points3D(object):
    def __init__(self, xyz):
        self.X, self.Y, self.Z = xyz
        self.shape = self.X.shape

        self.X_flat = np.ravel(self.X)
        self.Y_flat = np.ravel(self.Y)
        self.Z_flat = np.ravel(self.Z)

    @property
    def x_y_z_flat(self):
        return self.X_flat, self.Y_flat, self.Z_flat

    @property
    def XYZ(self):
        return np.vstack((self.X_flat, self.Y_flat, self.Z_flat)).T

    @property
    def XYZ_T(self):
        return np.vstack((self.X_flat, self.Y_flat, self.Z_flat))

    def copy(self):
        XYZ_tuple = (np.copy(self.X), np.copy(self.Y), np.copy(self.Z))
        return Points3D(XYZ_tuple)

    def findPointsAbove(self, n, a, copy=True):
        '''find points above a plane defined by Hessian Form n * x = a
           n: normal vector
           a: distance from origin
        '''
    
        b = np.dot(self.XYZ, n)
    
        if copy:
            iSelect = np.where(b > a)
            XYZ = self.XYZ[iSelect, :].squeeze()
            XYZ_tuple = np.hsplit(XYZ, 3)
            
            return Points3D(XYZ_tuple)
        else:
            iSelect = np.where(b < a)
            self.XYZ[iSelect, :] = np.NaN

            self.Z_flat[iSelect] = np.NaN
            
            return self
            
    
    def findPointsBelow(self, n, a, copy=True):
        '''find points below a plane defined by Hessian Form n * x = a
           n: normal vector
           a: distance from origin
        '''
        
        b = np.dot(self.XYZ, n)

        if copy:    
            iSelect = np.where(b < a)
            XYZ = self.XYZ[iSelect, :].squeeze()
            XYZ_tuple = np.hsplit(XYZ, 3)
            
            return Points3D(XYZ_tuple)
        else:
            iSelect = np.where(b > a)
            self.XYZ[iSelect, :] = np.NaN

            self.Z_flat[iSelect] = np.NaN
            
            return self
            


    def findPointsInAxisRange(self, lim, **kwargs):
        '''find points within axis limits
           lim: tuple of minimum and maximum value
        '''
        
        axis = 0
        copy = True
        
        for key, value in kwargs.items():
            if key == 'axis':
                axis = value
            elif key == 'copy':
                copy = value
        
        if copy:        
            iSelect = np.all(
                (lim[0] < self.XYZ[:,axis], self.XYZ[:,axis] < lim[1]),
                axis = 0)
            
            XYZ = self.XYZ[iSelect]
            XYZ_tuple = np.hsplit(XYZ, 3)
            
            return Points3D(XYZ_tuple)
        else:
            iSelect = np.where(self.XYZ[:,axis] < lim[0])
            self.Z_flat[iSelect] = np.NaN

            iSelect = np.where(lim[1] < self.XYZ[:,axis])
            self.Z_flat[iSelect] = np.NaN
                    
            return self

    def findPointsInRange(self, n, a, tol, copy=True):
        '''find points in a plane defined by Hessian Form n * x = a
           n: normal vector
           a: distance from origin
           tol: distance tolerance
        '''
        
        b = np.dot(self.XYZ, n)
    
        
        if copy:
            isInRange = np.abs(a - b) < tol
            iSelect = np.where(isInRange)
            XYZ = self.XYZ[iSelect]
            XYZ_tuple = np.hsplit(XYZ, 3)
            return Points3D(XYZ_tuple)
        else:
            isNotInRange = np.abs(a - b) > tol
            iSelect = np.where(isNotInRange)
            self.XYZ[iSelect] = np.NaN
            return self

    def findPointsOutsideRange(self, n, a, tol, copy=True):
        '''find points in a plane defined by Hessian Form n * x = a
           n: normal vector
           a: distance from origin
           tol: distance tolerance
        '''
        
        b = np.dot(self.XYZ, n)
        
        if copy:
            pass
        else:
            isInRange = np.abs(a - b) < tol
            iSelect = np.where(isInRange)
            self.XYZ[iSelect] = np.NaN
            self.Z_flat[iSelect] = np.NAN
            return self

    def finite(self):
        X_finite = self.X[np.isfinite(self.Z)]
        Y_finite = self.Y[np.isfinite(self.Z)]
        Z_finite = self.Z[np.isfinite(self.Z)]        

        return Points3D((X_finite, Y_finite, Z_finite))            

    def fitPlane(self):
        n, a = fitPlane_XYZ(self.XYZ)
        return n, a
        
    def rotate_v_v(self, v0, v1):
        q = Quaternion.from_v_v(v0, v1)
        R = q.as_rotation_matrix()
        XYZ = np.array(R * self.XYZ.T).T

        XYZ_tuple = np.hsplit(XYZ, 3)
        
        return Points3D(XYZ_tuple)
    
    def translate(self, v):
        XYZ = self.XYZ + v
        XYZ_tuple = np.hsplit(XYZ, 3)
        return Points3D(XYZ_tuple)
        