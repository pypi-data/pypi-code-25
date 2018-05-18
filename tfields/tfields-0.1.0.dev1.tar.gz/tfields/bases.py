#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
Tools for sympy coordinate transformation
"""
import tfields
import numpy as np
import sympy
import sympy.diffgeom
from six import string_types
import warnings

CARTESIAN = 'cartesian'
CYLINDER = 'cylinder'
SPHERICAL = 'spherical'

m = sympy.diffgeom.Manifold('M', 3)
patch = sympy.diffgeom.Patch('P', m)

# cartesian
x, y, z = sympy.symbols('x, y, z')
cartesian = sympy.diffgeom.CoordSystem(CARTESIAN, patch, ['x', 'y', 'z'])

# cylinder
R, Phi, Z = sympy.symbols('R, Phi, Z')
cylinder = sympy.diffgeom.CoordSystem(CYLINDER, patch, ['R', 'Phi', 'Z'])
cylinder.connect_to(cartesian,
                    [R, Phi, Z],
                    [R * sympy.cos(Phi),
                     R * sympy.sin(Phi),
                     Z],
                    inverse=False,
                    fill_in_gaps=False)
cartesian.connect_to(cylinder,
                     [x, y, z],
                     [sympy.sqrt(x**2 + y**2),
                      sympy.Piecewise(
                          (sympy.pi, ((x < 0) & sympy.Eq(y, 0))),
                          (0., sympy.Eq(sympy.sqrt(x**2 + y**2), 0)),
                          (sympy.acos(x / sympy.sqrt(x**2 + y**2)), True)),
                      z],
                     inverse=False,
                     fill_in_gaps=False)

# spherical
r, phi, theta = sympy.symbols('r, phi, theta')
spherical = sympy.diffgeom.CoordSystem(SPHERICAL, patch, ['r', 'phi', 'theta'])
spherical.connect_to(cartesian,
                     [r, phi, theta],
                     [r * sympy.cos(phi) * sympy.sin(theta),
                      r * sympy.sin(phi) * sympy.sin(theta),
                      r * sympy.cos(theta)],
                     inverse=False,
                     fill_in_gaps=False)
cartesian.connect_to(spherical,
                     [x, y, z],
                     [sympy.sqrt(x**2 + y**2 + z**2),
                      sympy.Piecewise(
                          (0., (sympy.Eq(x, 0) & sympy.Eq(y, 0))),
                          (sympy.atan(y / x), True)),
                      sympy.Piecewise(
                          (0., sympy.Eq(x**2 + y**2 + z**2, 0)),
                          # (0., (sympy.Eq(x, 0) & sympy.Eq(y, 0) & sympy.Eq(z, 0))),
                          (sympy.acos(z / sympy.sqrt(x**2 + y**2 + z**2)), True))],
                     inverse=False,
                     fill_in_gaps=False)


def getCoordSystem(base):
    """
    Args:
        base (str or sympy.diffgeom.getCoordSystem)
    Return:
        sympy.diffgeom.getCoordSystem
    """
    if isinstance(base, string_types):
        base = getattr(tfields.bases, base)
    if not isinstance(base, sympy.diffgeom.CoordSystem):
        raise TypeError("Wrong type of coordSystem base.")
    return base


def getCoordSystemName(base):
    """
    Args:
        base (str or sympy.diffgeom.getCoordSystem)
    Returns:
        str: name of base
    """
    if isinstance(base, sympy.diffgeom.CoordSystem):
        base = str(getattr(base, 'name'))
    # if not (isinstance(base, string_types) or base is None):
    #     baseType = type(base)
    #     raise ValueError("Coordinate system must be string_type."
    #                      " Retrieved value '{base}' of type {baseType}."
    #                      .format(**locals()))
    return base


def lambdifiedTrafo(baseOld, baseNew):
    """
    Args:
        baseOld (sympy.CoordSystem)
        baseNew (sympy.CoordSystem)

    Examples:
        >>> import numpy as np
        >>> import tfields

        Transform cartestian to cylinder or spherical
        >>> a = np.array([[3,4,0]])

        >>> trafo = tfields.bases.lambdifiedTrafo(tfields.bases.cartesian,
        ...                                       tfields.bases.cylinder)
        >>> new = np.concatenate([trafo(*coords).T for coords in a])
        >>> assert new[0, 0] == 5

        >>> trafo = tfields.bases.lambdifiedTrafo(tfields.bases.cartesian,
        ...                                       tfields.bases.spherical)
        >>> new = np.concatenate([trafo(*coords).T for coords in a])
        >>> assert new[0, 0] == 5

    """
    coords = tuple(baseOld.coord_function(i) for i in range(baseOld.dim))
    f = sympy.lambdify(coords,
                       baseOld.coord_tuple_transform_to(baseNew,
                                                        list(coords)),
                       modules='numpy')
    return f


def transform(array, baseOld, baseNew):
    """
    Examples:
        Transform cylinder to spherical. No connection is defined so routing via
        cartesian
        >>> import numpy as np
        >>> import tfields
        >>> b = np.array([[5, np.arctan(4. / 3), 0]])
        >>> newB = tfields.bases.transform(b, 'cylinder', 'spherical')
        >>> assert newB[0, 0] == 5
        >>> assert round(newB[0, 1], 10) == round(b[0, 1], 10)

    """

    baseOld = getCoordSystem(baseOld)
    baseNew = getCoordSystem(baseNew)
    if baseNew not in baseOld.transforms:
        for baseTmp in baseNew.transforms:
            if baseTmp in baseOld.transforms:
                tmpArray = transform(array, baseOld, baseTmp)
                return transform(tmpArray, baseTmp, baseNew)
        raise ValueError("Trafo not found.")

    trafo = tfields.bases.lambdifiedTrafo(baseOld, baseNew)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message="invalid value encountered in double_scalars")
        new = np.concatenate([trafo(*coords).T for coords in array])
    return new


if __name__ == '__main__':  # pragma: no cover
    import doctest
    doctest.testmod()
