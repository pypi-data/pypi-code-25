# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
---
Lattice objects describing a lattice of points.

Included are methods to select sublattices as cubes, sphere or side of planes.

The small angle scattering can is calculated by js.ff.cloudScattering.

The same method can be used to calculate the wide angle scattering with bragg peaks
using larger scattering vectors.


**Examples**

A hollow sphere cut to a wedge.
::

 import jscatter as js
 import numpy as np
 grid= js.lattice.scLattice(1/2.,2*8)
 grid.inSphere(6)
 grid.inSphere(-4)
 grid.limit2Cube(6,6,6)
 grid.planeSide([1,1,1])
 grid.planeSide([1,-1,-1])
 grid.show()

 q=js.loglist(0.01,5,600)
 ffe=js.ff.cloudScattering(q,grid.points,relError=0.02,rms=0.1)
 p=js.grace()
 p.plot(ffe)

A comparison of sc, bcc and fcc nanoparticles (takes a while )
::

 import jscatter as js
 import numpy as np
 q=js.loglist(0.01,35,1500)
 q=np.r_[js.loglist(0.01,3,200),3:40:800j]
 unitcelllength=1.5
 N=8

 scgrid= js.lattice.scLattice(unitcelllength,N)
 sc=js.ff.cloudScattering(q,scgrid.points,relError=50,rms=0.05)
 bccgrid= js.lattice.bccLattice(unitcelllength,N)
 bcc=js.ff.cloudScattering(q,bccgrid.points,relError=50,rms=0.05)
 fccgrid= js.lattice.fccLattice(unitcelllength,N)
 fcc=js.ff.cloudScattering(q,fccgrid.points,relError=50,rms=0.05)

 p=js.grace(1.5,1)
 # smooth with Gaussian to include instrument resolution
 p.plot(sc.X,js.formel.smooth(sc,10, window='gaussian'),legend='sc')
 p.plot(bcc.X,js.formel.smooth(bcc,10, window='gaussian'),legend='bcc')
 p.plot(fcc.X,js.formel.smooth(fcc,10, window='gaussian'),legend='fcc')

 q=q=js.loglist(1,35,100)
 p.plot(q,(1-np.exp(-q*q*0.05**2))/scgrid.shape[0],li=1,sy=0,le='sc diffusive')
 p.plot(q,(1-np.exp(-q*q*0.05**2))/bccgrid.shape[0],li=2,sy=0,le='bcc diffusive')
 p.plot(q,(1-np.exp(-q*q*0.05**2))/fccgrid.shape[0],li=3,sy=0,le='fcc diffusive')

 p.title('Comparison sc, bcc, fcc lattice for a nano cube')
 p.yaxis(scale='l',label='I(Q)')
 p.xaxis(scale='l',label='Q / A\S-1')
 p.legend(x=0.03,y=0.001,charsize=1.5)
 p.text('cube formfactor',x=0.02,y=0.05,charsize=1.4)
 p.text('Bragg peaks',x=4,y=0.05,charsize=1.4)
 p.text('diffusive scattering',x=4,y=1e-6,charsize=1.4)

END
"""
from __future__ import division
from __future__ import print_function

import numpy as np
from numpy import linalg as la
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
except:
    pass
try:
    from . import fscatter
    useFortran=True
except:
    useFortran = False

from . import formel


class lattice(object):

    isLattice=True
    def __init__(self):
        """
        Create an arbitrary lattice

        """
        pass

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, item, value):
        if self[item].shape==np.shape(value):
            self.points[item] = value
        else:
            raise TypeError('Wrong shape of given value')

    @property
    def dimension(self):
        return self.points.shape[1]-1

    @property
    def X(self):
        """X coordinates"""
        return self.points[:,0]

    @property
    def Y(self):
        """Y coordinates"""
        return self.points[:, 1]

    @property
    def Z(self):
        """Z coordinates"""
        return self.points[:, 2]

    @property
    def b(self):
        """Scattering length"""
        return self.points[:, 3]

    @property
    def shape(self):
        return self.array.shape

    @property
    def type(self):
        return self._type

    @property
    def array(self):
        """Coordinates and scattering length as array"""
        return np.array(self.points)

    def filter(self,funktion):
        """
        Filter lattice points according to a function.

        The existing points in the lattice size are tested.

        Parameters
        ----------
        funktion : function returning bool
            Function to select lattice points.
            The function is applied with the point coordinates (array) as input.
            This corresponds to .points[:,:3]

        Returns
        -------
            array

        Examples
        --------
        To select points inside of a sphere with radius 50 around [0,0,0]:
        ::

         grid.filter(lambda xyz: np.sum(xyz**2)<50**2)


        """
        return self.points[[funktion(point) for point in self.points[:,:3]]]

    def centerOfMass(self):
        """
        CenterOf mass
        """
        return self.points[:,:3].mean(axis=0)

    def numberOfAtoms(self):
        """
        Number of Atoms
        """
        return self.points.shape[0]

    def limit2Cube(self,a,b,c):
        """
        Cut at cube with edges at

        Parameters
        ----------
        a,b,c : float
            Cut at +-[a,0,0],+-[0,b,0],+-[0,0,c]

        Returns
        -------

        """
        choose=(abs(self.X)<a) & (abs(self.Y)<b) & (abs(self.Z)<c)
        self.points=self.points[choose]

    def planeSide(self,vector,invert=False):
        """
        Select points on one side of a plane.

        Parameters
        ----------
        vector : list 3x float
            Vector from origin to plane, perpendicular to plane.
        invert : bool
            False choose points at origin side. True other side.

        """
        v=np.array(vector)
        vv=(v ** 2).sum() ** 0.5
        v=v/vv
        if invert:
            choose = np.dot(self.points[:,:3] , v) >= vv
        else:
            choose = np.dot(self.points[:,:3] , v) <= vv
        self.points = self.points[choose]

    def move(self,vector):
        """
        Move all points by vector.

        Parameters
        ----------
        vector : list of 3 float or array
            Vector to shift the points.

        """
        self.points[:,:3]=self.points[:,:3]+np.array(vector)

    def inSphere(self,R):
        """
        Choose lattice points in sphere

        Parameters
        ----------
        R: float
            Radius of sphere around origin.
            If negative the points outside are choosen

        """
        if R>0:
            choose=np.sum((self.points[:,:3]**2),axis=1)<R**2
        else:
            choose = np.sum((self.points[:,:3]**2), axis=1) > R**2
        self.points=self.points[choose]

    def show(self,R=None):
        """
        Show the lattice in matplotlib.

        Parameters
        ----------
        R : float,None
            Radius around origin to show.

        Returns
        -------
         fig handle

        """
        if R is None:
            points=self.points
        else:
            choose=np.sum((self.points[:,:3]**2),axis=1)<R**2
            points=self.points[choose]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(points[:,0],points[:,1],points[:,2],color="k",s=20)
        try:
            for v in self.latticeVectors:
                ax.plot([0,v[0]],[0,v[1]],[0,v[2]],color='g')
        except:
            pass
        try:
            for v in self.unitCellAtomPositions:
                if (v**2).sum()==0:
                    pass
                ax.plot([0,v[0]],[0,v[1]],[0,v[2]],color='b')
        except:
            pass

        ax.set_aspect("equal")
        plt.tight_layout()
        plt.show(block=False)
        return fig

    def getReciprocalLattice(self, size=2):
        print('Only for rhombic lattices')
        return None

    def rotate2hkl(self,grid, h,k,l):
        print('Only for rhombic lattices')
        return None

class pseudoRandomLattice(lattice):

    def __init__(self,size,numberOfPoints,b=None,seed=None):
        """
        Create a  lattice with a pseudo random distribution of points.

        Allows to create 1D, 2D or 3D pseudo random latices.
        The Halton sequence is used with skiping the first seed elements of the Halton sequence.

        Parameters
        ----------
        size :3x float
            Size of the lattice for each dimension relative to origin.
        numberOfPoints : int
            Number of points.
        b : float,array
            Scattering length of atoms. If arary the sequence is repeated to fill N atoms.
        seed : None, int
            Seed for the Halton sequence by skiping the first seed elements of the sequence.
            If None an random integer between 10 and 1e6 is choosen.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.pseudoRandomLattice([5,5,5],3000)
         fig=grid.show()

        """
        self._makeLattice(size, numberOfPoints,b,seed)
        self._type='pseudorandom'

    def _makeLattice(self, size, N ,pb=None ,skip=None ):
        if pb is None:
            pb=1
        dim=np.shape(size)[0]
        if skip is None:
            skip=np.random.randint(10,1000000)
        seq=fscatter.pseudorandom.halton_sequence(skip,skip+N-1,dim).T
        seq=seq*np.array(size)
        if dim in [1,2]:
            seq=np.c_[seq,np.zeros((N,3-dim))]
        self.points=np.c_[seq,np.tile(pb,N)[:N]]


class rhombicLattice(lattice):

    isRhombic=True

    def __init__(self, latticeVectors, size, unitCellAtoms=None,b=None):
        """
        Create a rhombic lattice with specified unit cell atoms.

        Allows to create 1D, 2D or 3D latices by using 1, 2 or 3 latticeVectors.

        Parameters
        ----------
        latticeVectors : list of array 3x1
            Lattice vectors defining the translation of the unit cell along its principal axes.
        size :3x integer or integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        unitCellAtoms : list of 3x1 array, None=[0,0,0]
            Position vectors of atoms in the unit cell in relative units of the lattice vectors [0<x<1].
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array
            .unitCellVolume         V = a1*a2 x a3 with latticeVectors a1, a2, a3;  if existing.

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         # cubic lattice with diatomic base
         grid=js.sf.rhombicLattice([[1,0,0],[0,1,0],[0,0,1]],[3,3,3],[[-0.1,-0.1,-0.1],[0.1,0.1,0.1]],[1,2])
         grid.show(1.5)

        """
        if len(latticeVectors) != len(size):
            raise TypeError('size and latticeVectors not compatible. Check dimension!')
        if unitCellAtoms is None:
            unitCellAtoms = [np.r_[0, 0, 0]]
        size=np.trunc(size)
        if b is None:
            b=[1]*len(unitCellAtoms)
        self.unitCellAtoms_b=b

        # calc reciprocal vectors
        if len(latticeVectors)==3:
            V=np.dot(latticeVectors[0],np.cross(latticeVectors[1],latticeVectors[2]))
            self.unitCellVolume = V
            self.reciprocalVectors = []
            self.reciprocalVectors.append(2 * np.pi / V * np.cross(latticeVectors[1], latticeVectors[2]))
            self.reciprocalVectors.append(2 * np.pi / V * np.cross(latticeVectors[2], latticeVectors[0]))
            self.reciprocalVectors.append(2 * np.pi / V * np.cross(latticeVectors[0], latticeVectors[1]))
        elif len(latticeVectors)==2:
            R=formel.rotationMatrix(np.r_[0,0,1],np.pi/2)
            self.reciprocalVectors = []
            v0=np.dot(R, latticeVectors[0])
            v1 = np.dot(R, latticeVectors[1])
            self.unitCellVolume = np.dot(v0,v1)
            self.reciprocalVectors.append(2 * np.pi  * v1/np.dot(latticeVectors[0],v1))
            self.reciprocalVectors.append(2 * np.pi  * v0/np.dot(latticeVectors[1],v0))
        elif len(latticeVectors)==1:
            R = formel.rotationMatrix(np.r_[0, 0, 1], np.pi / 2)
            v0 = np.dot(R, latticeVectors[0])
            self.unitCellVolume = la.norm(v0)
            self.reciprocalVectors = []
            self.reciprocalVectors.append(2 * np.pi *v0/la.norm(v0)**2)
        self.latticeVectors=latticeVectors
        self.size=size
        self._makeLattice( self.latticeVectors, size, unitCellAtoms, self.unitCellAtoms_b)
        self._type='rhombic'

    def _makeLattice(self, latticeVectors, size, unitCellAtoms=None,pb=None):
        abc=latticeVectors[0]*np.r_[-size[0]:size[0]+1][:,None]
        if len(size)>1:
            abc = abc+(latticeVectors[1]*np.r_[-size[1]:size[1]+1][:,None])[:,None]
        if len(size) > 2:
            abc = abc + (latticeVectors[2]*np.r_[-size[2]:size[2]+1][:,None,None])[:,None,None]
        abc=abc.reshape(-1,3)
        abc=np.c_[(abc,np.zeros(abc.shape[0]))]
        uCA=np.einsum('il,ji',latticeVectors,unitCellAtoms)
        self.points=np.vstack([abc + np.r_[ev,b] for ev,b in zip(uCA,pb)])
        self.unitCellAtoms=unitCellAtoms

    @property
    def unitCellAtomPositions(self):
        """
        Absolute positions of unit cell atoms.

        """
        return np.einsum('il,ji',self.latticeVectors,self.unitCellAtoms)

    def getReciprocalLattice(self,size=2):
        """
        Reciprocal lattice of given size with peak scattering intensity.

        Parameters
        ----------
        size : 3x int, default 3
            Number of reciprocal lattice points in each direction (+- direction).

        Returns
        -------
            Array [N x 4] with
             reciprocal lattice vectors                 [:,:3]
             corresponding structure factor fhkl**2>0   [:, 3]

        """
        if isinstance(size,int):
            size=[size]*3
        size=np.trunc(size)
        # create lattice
        bbb =        self.reciprocalVectors[0] * np.r_[-size[0]:size[0] + 1][:, None]
        hkl =        np.r_[1,0,0]              * np.r_[-size[0]:size[0] + 1][:, None]
        if len(self.reciprocalVectors)>1:
            bbb = bbb + (self.reciprocalVectors[1] * np.r_[-size[1]:size[1] + 1][:, None])[:, None]
            hkl = hkl + (np.r_[0,1,0]              * np.r_[-size[1]:size[1] + 1][:, None])[:, None]
        if len(self.reciprocalVectors) > 2:
            bbb = bbb + (self.reciprocalVectors[2] * np.r_[-size[2]:size[2] + 1][:, None, None])[:, None, None]
            hkl = hkl + (np.r_[0,0,1]              * np.r_[-size[2]:size[2] + 1][:, None, None])[:, None, None]

        bbb = bbb.reshape(-1, 3)
        hkl = hkl.reshape(-1, 3)
        # calc structure factor
        f2hkl=self._f2hkl(hkl)
        # selection rule
        choose=[f2hkl > 1e-10*f2hkl.max() ]

        return  np.c_[bbb[choose],f2hkl[choose]]

    def getRadialReciprocalLattice(self,size,includeZero=False):
        """
        Get radial distribution of Bragg peaks with structure factor and multiplicity.

        Parameters
        ----------
        size : int
            Size of the lattice as maximum included Miller indices.
        includeZero : bool
            Include q=0 peak

        Returns
        -------
            3x list of [unique q values, structure factor fhkl(q)**2, multiplicity mhkl(q)]

        """
        qxyzb=self.getReciprocalLattice(size)
        qr=la.norm(qxyzb[:,:3],axis=1)
        f2hkl=qxyzb[:,3]
        tol=1e7
        qrunique,qrindex,qrcount=np.unique(np.floor(qr*tol)/tol,return_index=True,return_inverse=False,return_counts=True)
        # q values of unique peaks, scattering strenght f2hkl, multiplicity as number of unique peaks from 3D count
        if includeZero:
            return qrunique,f2hkl[qrindex],qrcount
        else:
            return qrunique[1:], f2hkl[qrindex][1:], qrcount[1:]

    def _f2hkl(self,hkl):
        """
        Structure factor f**2_hkl which includes the extiction rules.

        """
        pb=np.array(self.unitCellAtoms_b)[:,None]
        hxkylz=np.einsum('ij,lj',self.unitCellAtoms,hkl)
        fhkl=(pb*np.exp(2j*np.pi*hxkylz)).sum(axis=0)
        return (fhkl*fhkl.conj()).real

    def rotate2hkl(self,grid, h,k,l):
        """
        Rotate a grid to a plane perpendicular to hkl direction.

        Parameters
        ----------
        grid : array Nx3
            Grid points
        h,k,l : integer, float
            Miller indices indicating the direction where to rotate to.

        Returns
        -------
            grid points array 4xN

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         R=8
         N=10
         qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
         qxyz=np.c_[qxy,np.zeros(N**2)]
         fccgrid = js.lattice.fccLattice(2.1, 1)
         xyz=fccgrid.rotate2hkl(qxyz,1,1,1)
         p=js.mpl.scatter3d(xyz[:,0],xyz[:,1],xyz[:,2])
         p.axes[0].scatter(fccgrid.X,fccgrid.Y,fccgrid.Z)


        """
        # hkl direction
        vhkl=h*self.latticeVectors[0]+k*self.latticeVectors[1]+l*self.latticeVectors[2]
        # vector perpendicular to grid plane
        center=grid.mean(axis=0)
        centerdistance=((grid-center)**2).sum(axis=1)**0.5
        isort=np.argsort(centerdistance)
        # first vector in grid close to center, then next with cross >0
        v1=grid[isort[0]]-grid[isort[1]]
        i=2
        while True:
            v2=grid[isort[0]]-grid[isort[i]]
            v3=np.cross(v1,v2)
            # test if >0 then it is perpendicular to plane
            if la.norm(v3)>0:
                break
            else:i+=1
        rotvector=np.cross(vhkl,v3)/la.norm(v3)/la.norm(vhkl)
        angle=np.arccos(np.clip(np.dot(vhkl/la.norm(vhkl), v3/la.norm(v3)), -1.0, 1.0))
        R=formel.rotationMatrix(rotvector,angle)
        Rgrid=np.einsum('ij,kj->ki',R,grid)
        return Rgrid


class bravaisLattice(rhombicLattice):

    def __init__(self, latticeVectors, size):
        """
        Create a bravais lattice. Lattice with one atom in the unit cell.

        See rhombicLattice for methods and attributes.

        Parameters
        ----------
        latticeVectors : list of array 1x3
            Lattice vectors defining the translation of the unit cell along its principal axes.
        size :3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points asnumpy array

        """
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms=[np.r_[0,0,0]])
        self._type = 'bravais'


class scLattice(bravaisLattice):

    def __init__(self, abc, size):
        """
        Simple Cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.sf.bccLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size,(int,float)):
            size = [size]*3
        bravaisLattice.__init__(self, latticeVectors, size)
        self._type = 'sc'


class bccLattice(rhombicLattice):

    def __init__(self, abc, size,b=None):
        """
        Body centered cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.bccLattice(1.2,1)
         grid.show(2)

        """
        unitCellAtoms = [np.r_[0, 0, 0], np.r_[0.5, 0.5, 0.5]]
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size,(int,float)):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms,b)
        self._type = 'bcc'


class fccLattice(rhombicLattice):

    def __init__(self, abc, size):
        """
        Face centered cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.sf.fccLattice(1.2,1)
         grid.show(2)

        """
        unitCellAtoms = [np.r_[0,   0,   0],
                         np.r_[0, 0.5, 0.5],
                         np.r_[0.5, 0, 0.5],
                         np.r_[0.5, 0.5, 0]]
        latticeVectors = [abc *np.r_[1., 0., 0.],
                          abc *np.r_[0., 1., 0.],
                          abc *np.r_[0., 0., 1.]]
        if isinstance(size,(int,float)):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms)
        self._type = 'fcc'


class diamondLattice(rhombicLattice):

    def __init__(self, abc, size):
        """
        Diamond cubic lattice with 8 atoms in unit cell.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.diamondLattice(1.2,1)
         grid.show(2)

        """
        unitCellAtoms = [np.r_[0,   0,   0],
                         np.r_[0.5, 0.5,0],
                         np.r_[0, 0.5, 0.5],
                         np.r_[0.5, 0, 0.5],
                         np.r_[1 / 4., 1 / 4., 1 / 4.],
                         np.r_[3 / 4., 3 / 4., 1 / 4.],
                         np.r_[1 / 4., 3 / 4., 3 / 4.],
                         np.r_[3 / 4., 1 / 4., 3 / 4.]]
        latticeVectors = [abc *np.r_[1., 0., 0.],
                          abc *np.r_[0., 1., 0.],
                          abc *np.r_[0., 0., 1.]]
        if isinstance(size,(int,float)):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms)
        self._type = 'diamond'


class hexLattice(rhombicLattice):

    def __init__(self, ab,c, size):
        """
        Hexagonal lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab,c : float
            Point distance.
            ab is distance in hexagonal plane, c perpendicular.
            For c/a = (8/3)**0.5 the hcp structure
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.sf.hexLattice(1.,2,[2,2,2])
         grid.show(2)

        """

        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5*ab, 3**0.5/2*ab, 0.],
                          np.r_[0., 0., c]]
        unitCellAtoms = [      np.r_[0, 0, 0] ]
        if isinstance(size,(int,float)):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms)
        self._type = 'hex'


class hcpLattice(rhombicLattice):

    def __init__(self, ab, size):
        """
        Hexagonal closed packed lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Point distance.
            ab is distance in hexagonal plane, c = ab* (8/3)**0.5
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.sf.hcpLattice(1.2,[3,3,1])
         grid.show(2)

        """
        c = ab* (8/3.)**0.5
        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5*ab, 3**0.5/2*ab, 0.],
                          np.r_[0., 0., c]]
        unitCellAtoms = [   np.r_[0, 0, 0],
                            np.r_[1/3. , 1/3.,0.5 ]]

        if isinstance(size,(int,float)):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms)
        self._type = 'hcp'


class sqLattice(bravaisLattice):

    def __init__(self, ab, size):
        """
        Simple 2D square lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Point distance.
        size : 2x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.sqLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [ab * np.r_[1., 0., 0.],
                          ab * np.r_[0., 1., 0.]]
        if isinstance(size,(int,float)):
            size = [size]*2
        bravaisLattice.__init__(self, latticeVectors, size)
        self._type = 'sq'


class hexLattice(bravaisLattice):

    def __init__(self, ab, size):
        """
        Simple 2D hexagonal lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Point distance.
        size : 2x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.hexLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5*ab, 3**0.5/2*ab, 0.]]
        if isinstance(size,(int,float)):
            size = [size]*2
        bravaisLattice.__init__(self, latticeVectors, size)
        self._type = 'hex'


class lamLattice(bravaisLattice):

    def __init__(self, a, size):
        """
        1D lamellar lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        a : float
            Point distance.
        size : 2x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.lamLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [np.r_[a, 0., 0.]]
        if isinstance(size,(int,float)):
            size = [size]*1
        bravaisLattice.__init__(self, latticeVectors, size)
        self._type = 'lam'

