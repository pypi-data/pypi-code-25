#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
contains interaction methods for sympy and numpy
"""
import numpy as np
import sympy


def getMask(array, cutExpression=None, coords=None):
    """
    Linking sympy and numpy by retrieving a mask according to the cutExpression

    Args:
        array (numpy ndarray)
        cutExpression (sympy logical expression)
        coordSys (str): coordSys to evaluate the expression in.
    Returns: np.array which is True, where cutExpression evaluates True.
    Examples:
        >>> import sympy
        >>> import numpy as np
        >>> import tfields
        >>> x, y, z = sympy.symbols('x y z')

        >>> a = np.array([[1., 2., 3.], [4., 5., 6.], [1, 2, -6], [-5, -5, -5], [1,0,-1], [0,1,-1]])
        >>> assert np.array_equal(tfields.getMask(a, x > 0),
        ...                       np.array([ True, True, True, False, True, False]))

        And combination
        >>> assert np.array_equal(tfields.getMask(a, (x > 0) & (y < 3)),
        ...                       np.array([True, False, True, False, True, False]))

        Or combination
        >>> assert np.array_equal(tfields.getMask(a, (x > 0) | (y > 3)),
        ...                       np.array([True, True, True, False, True, False]))

        If array of other shape than (?, 3) is given, the coords need to be specified
        >>> a0, a1 = sympy.symbols('a0 a1')
        >>> assert np.array_equal(tfields.getMask([[0., 1.], [-1, 3]], a1 > 2,
        ...                                       coords=[a0, a1]),
        ...                       np.array([False,  True], dtype=bool))

    """
    if isinstance(array, list):
        array = np.array(array)
    if cutExpression is None:
        return np.full((array.shape[0]), False, dtype=bool)
    if len(array.shape) != 2:
        raise NotImplementedError("Array shape other than 2")
    if coords is None:
        if array.shape[1] == 3:
            coords = sympy.symbols('x y z')
        else:
            raise ValueError("coords are None and shape is not (?, 3)")

    elif len(coords) != array.shape[1]:
        raise ValueError("Length of coords is not {0} but {1}".format(array.shape[1], len(coords)))

    preMask = sympy.utilities.lambdify(coords,
                                       cutExpression,
                                       modules={'&': np.logical_and, '|': np.logical_or})

    mask = np.array([preMask(*x) for x in array], dtype=bool)

    return mask


if __name__ == '__main__':  # pragma: no cover
    import doctest
    doctest.testmod()
