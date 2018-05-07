'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 22, 2018
@author: Niels Lubbes
'''

from sage_interface import sage_matrix
from sage_interface import sage_vector
from sage_interface import sage_identity_matrix
from sage_interface import sage_QQ

from orbital.cossin.cos_sin import get_cs


def get_rot_mat( dim, i, j, angle ):
    '''    
    Constructs a higher dimensional rotation matrix.
        
    Parameters
    ----------
    dim: int
        Width and height of square matrix.        
    i: int
    j: int
    angle: int
        Angle in [0,360].
        
    Returns
    -------
    sage_matrix
        A matrix which looks like a square identity matrix of
        width "dim", except the entries 
            (i,i), (i,j), 
            (j,i), (j,j)
        define the rotation matrix:
            [ cos(angle) -sin(angle) ]
            [ sin(angle)  cos(angle) ]
    '''

    c, s = get_cs( angle )


    mat = []
    for a in range( dim ):
        row = []
        for b in range( dim ):
            e = 0
            if a == b: e = 1
            if a != b: e = 0
            if ( a, b ) == ( i, i ): e = c
            if ( a, b ) == ( i, j ): e = -s
            if ( a, b ) == ( j, i ): e = s
            if ( a, b ) == ( j, j ): e = c
            row += [e]
        mat += [row]

    return sage_matrix( mat )


def get_rot_S3( a01, a02, a03, a12, a13, a23 ):
    '''
    Constructs a rotation matrix for S^3.
        
    Parameters
    ----------
    a01 : int
        An integer in [0,360] denoting the angle.
    a02 : int
    a03 : int
    a12 : int
    a13 : int
    a23 : int
    
    Returns
    -------
    sage_matrix
        A 5x5 matrix that rotates the projective closure of S^3 in 
        projective 4-space along the angle parameters. 
    '''

    M = sage_identity_matrix( 5 )
    M *= get_rot_mat( 5, 0, 1, a01 )
    M *= get_rot_mat( 5, 0, 2, a02 )
    M *= get_rot_mat( 5, 0, 3, a03 )
    M *= get_rot_mat( 5, 1, 2, a12 )
    M *= get_rot_mat( 5, 1, 3, a13 )
    M *= get_rot_mat( 5, 2, 3, a23 )

    return sage_matrix( M )


def get_trn_S3( x0, y0, z0, s ):
    '''
    Constructs a translation matrix for S3.
    Via a stereographic projection these transformations 
    correspond to translations and scalings in Euclidean 3-space.
    
    Parameters
    ----------
    x0: sage_QQ
        Translation parameter in x-direction.
    y0: sage_QQ
        Translation parameter in y-direction.
    z0: sage_QQ
        Translation parameter in z-direction.
    s: sage_QQ
        Scaling factor s.
    
    Returns
    -------
    sage_matrix
        Transformation matrix that preserves the projective closure
        of S^3 in P^4.    
    '''
    M = []

    T = s ** 2 * ( x0 ** 2 + y0 ** 2 + z0 ** 2 )

    M += [[2 * s, 0, 0, -2 * s * x0, 2 * s * x0]]
    M += [[0, 2 * s, 0, -2 * s * y0, 2 * s * y0]]
    M += [[0, 0, 2 * s, -2 * s * z0, 2 * s * z0]]
    M += [[2 * s ** 2 * x0, 2 * s ** 2 * y0, 2 * s ** 2 * z0, s ** 2 + 1 - T, s ** 2 - 1 + T]]
    M += [[2 * s ** 2 * x0, 2 * s ** 2 * y0, 2 * s ** 2 * z0, s ** 2 - 1 - T, s ** 2 + 1 + T]]

    return sage_matrix( M )


def get_xfer_S3( a01, a02, a03, a12, a13, a23, x0, y0, z0, s ):
    '''
    Constructs a 5x5 matrix that is an element of Aut(S^3) where S^3
    is the projective 3-sphere in projective 4-space. 

    This method is for convenience to obtain get_trn_S3 and get_rot_S3
    in one call.

    Parameters
    ----------
    a01,a02,a03,a12,a13,a23 : int
        Integers in [0,360] denoting rotation angles.
    x0: sage_QQ
        Translation parameter in x-direction.
    y0: sage_QQ
        Translation parameter in y-direction.
    z0: sage_QQ
        Translation parameter in z-direction.
    s: sage_QQ
        Scaling factor s.

    Returns
    -------
    sage_matrix
    '''

    M = sage_identity_matrix( 5 )
    M *= get_trn_S3( x0, y0, z0, s )
    M *= get_rot_S3( a01, a02, a03, a12, a13, a23 )

    return M


def get_hp_S3( v, w ):
    '''
    Computes the Hamiltonian product of two vectors 
    in the projectivized 3-sphere. We first consider 
    an affine chart where the last coordinate is nonzero.
    This chart is the unit 3-sphere in real 3-space
    and can be identified with the unit quaternions.  
    
    Parameters
    ----------
    v: sage_vector
    w: sage_vector
        
    Returns
    -------
    sage_vector
    '''
    q0, q1, q2, q3, q4 = list( v )
    r0, r1, r2, r3, r4 = list( w )

    a0 = q0 / q4;a1 = q1 / q4;a2 = q2 / q4;a3 = q3 / q4;
    b0 = r0 / r4;b1 = r1 / r4;b2 = r2 / r4;b3 = r3 / r4;

    lst = [ a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
            a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
            a0 * b2 + a2 * b0 + a3 * b1 - a1 * b3,
            a0 * b3 + a3 * b0 + a1 * b2 - a2 * b1,
            1 ]

    return sage_vector( lst )


def get_prj_S3( v ):
    '''
    Computes the stereographic projection of the coordinate
    followed by taking an affine chart. Thus this function
    defines a map from the projective 3-sphere to Euclidean 
    3-space.      
    
    Parameters
    ----------
    v: sage_vector
        A (parametrized) point in the projective 3-sphere. 
        The the projectivized coordinate has 5 entries.
    
    Returns
    -------
    list
            
    '''
    v0, v1, v2, v3, v4 = list( v )
    den = v3 - v4
    lst = [ v0 / den, v1 / den, v2 / den ]

    return lst


