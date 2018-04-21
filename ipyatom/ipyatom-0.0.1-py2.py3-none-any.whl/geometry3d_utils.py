"""
taken largely from: https://www.lfd.uci.edu/~gohlke/code/transformations.py.html
"""
import random
import math
import numpy
import numpy as np


def unit_vector(data, axis=None, out=None):
    """Return ndarray normalized by length, i.e. Euclidean norm, along axis.

    >>> v0 = np.random.random(3)
    >>> v1 = unit_vector(v0)
    >>> np.allclose(v1, v0 / np.linalg.norm(v0))
    True
    >>> v0 = np.random.rand(5, 4, 3)
    >>> v1 = unit_vector(v0, axis=-1)
    >>> v2 = v0 / np.expand_dims(np.sqrt(np.sum(v0*v0, axis=2)), 2)
    >>> np.allclose(v1, v2)
    True
    >>> v1 = unit_vector(v0, axis=1)
    >>> v2 = v0 / np.expand_dims(np.sqrt(np.sum(v0*v0, axis=1)), 1)
    >>> np.allclose(v1, v2)
    True
    >>> v1 = np.empty((5, 4, 3))
    >>> unit_vector(v0, axis=1, out=v1)
    >>> np.allclose(v1, v2)
    True
    >>> list(unit_vector([]))
    []
    >>> list(unit_vector([1]))
    [1.0]

    """
    if out is None:
        data = np.array(data, dtype=np.float64, copy=True)
        if data.ndim == 1:
            data /= math.sqrt(np.dot(data, data))
            return data
    else:
        if out is not data:
            out[:] = np.array(data, copy=False)
        data = out
    length = np.atleast_1d(np.sum(data*data, axis))
    np.sqrt(length, length)
    if axis is not None:
        length = np.expand_dims(length, axis)
    data /= length
    if out is None:
        return data


def is_same_transform(matrix0, matrix1):
    """Return True if two matrices perform same transformation.

    >>> is_same_transform(np.identity(4), np.identity(4))
    True
    >>> is_same_transform(np.identity(4), np.ones((4,4)))
    False

    """
    matrix0 = np.array(matrix0, dtype=np.float64, copy=True)
    matrix0 /= matrix0[3, 3]
    matrix1 = np.array(matrix1, dtype=np.float64, copy=True)
    matrix1 /= matrix1[3, 3]
    return np.allclose(matrix0, matrix1)


def rotation_matrix(angle, direction, point=None, in_radians=True):
    """Return matrix to rotate about axis defined by point and direction.

    Parameters
    ----------
    angle: float
    direction: np.array((3,))
    point: np.array((3,))
    in_radians: bool
        angle in radians, else degrees

    Examples
    --------
    >>> R = rotation_matrix(math.pi/2, [0, 0, 1], [1, 0, 0])
    >>> np.allclose(np.dot(R, [0, 0, 0, 1]), [1, -1, 0, 1])
    True
    >>> angle = (random.random() - 0.5) * (2*math.pi)
    >>> direc = np.random.random(3) - 0.5
    >>> point = np.random.random(3) - 0.5
    >>> R0 = rotation_matrix(angle, direc, point)
    >>> R1 = rotation_matrix(angle-2*math.pi, direc, point)
    >>> is_same_transform(R0, R1)
    True
    >>> R0 = rotation_matrix(angle, direc, point)
    >>> R1 = rotation_matrix(-angle, -direc, point)
    >>> is_same_transform(R0, R1)
    True
    >>> I = np.identity(4, np.float64)
    >>> np.allclose(I, rotation_matrix(math.pi*2, direc))
    True
    >>> np.allclose(2, np.trace(rotation_matrix(math.pi/2,
    ...                                               direc, point)))
    True

    >>> vectors = [3, 5, 0, 0]
    >>> axis = [4, 4, 1]
    >>> angle = math.degrees(1.2)
    >>> rot = rotation_matrix(angle, axis, in_radians=False)
    >>> print(np.dot(rot, vectors)[0:3].round(3))
    [ 2.749  4.772  1.916]


    """
    if not in_radians:
        angle = math.radians(angle)
    sina = math.sin(angle)
    cosa = math.cos(angle)
    direction = unit_vector(direction[:3])
    # rotation matrix around unit vector
    rot = np.diag([cosa, cosa, cosa])
    rot += np.outer(direction, direction) * (1.0 - cosa)
    direction *= sina
    rot += np.array([[0.0, -direction[2], direction[1]],
                      [direction[2], 0.0, -direction[0]],
                      [-direction[1], direction[0], 0.0]])
    output = np.identity(4)
    output[:3, :3] = rot
    if point is not None:
        # rotation not around origin
        point = np.array(point[:3], dtype=np.float64, copy=False)
        output[:3, 3] = point - np.dot(rot, point)
    return output


def align_rotation_matrix(v_init, v_final, point=None):
    """ compute the rotation matrix to align v1 to v2

    Parameters
    ----------
    v_init : np.array((3,))
    v_final : np.array((3,))
    point: None

    Examples
    --------
    >>> align_rotation_matrix([1,0,0],[0,1,0])
    array([[ 0., -1.,  0.,  0.],
           [ 1.,  0.,  0.,  0.],
           [ 0.,  0.,  1.,  0.],
           [ 0.,  0.,  0.,  1.]])

    """
    v_init = np.asarray(v_init, dtype=np.float64)
    v_final = np.asarray(v_final, dtype=np.float64)

    # Normalize vector length
    i_v_norm = v_init / np.linalg.norm(v_init)
    f_v_norm = v_final / np.linalg.norm(v_final)
    # Get axis
    uvw = np.cross(i_v_norm, f_v_norm)
    # compute trig values - no need to go through arccos and back
    rcos = np.dot(i_v_norm, f_v_norm)
    rsin = np.linalg.norm(uvw)
    # normalize and unpack axis
    if not np.isclose(rsin, 0):
        uvw /= rsin
    u, v, w = uvw
    # Compute rotation matrix
    rot = (
        rcos * np.eye(3) +
        rsin * np.array([
            [0, w, -v],
            [-w, 0, u],
            [v, -u, 0]]) +
        (1.0 - rcos) * uvw[:, None] * uvw[None, :]).T

    output = np.identity(4)
    output[:3, :3] = rot
    if point is not None:
        # rotation not around origin
        point = np.array(point[:3], dtype=np.float64, copy=False)
        output[:3, 3] = point - np.dot(rot, point)
    return output


def translation_matrix(direction):
    """Return matrix to translate by direction vector.

    >>> v = np.random.random(3) - 0.5
    >>> np.allclose(v, translation_matrix(v)[:3, 3])
    True

    """
    output = np.identity(4)
    output[:3, 3] = direction[:3]
    return output


def concatenate_matrices(*matrices):
    """Return concatenation of series of transformation matrices.
    NB: transformations are applied in reverse order

    >>> M = np.random.rand(16).reshape((4, 4)) - 0.5
    >>> np.allclose(M, concatenate_matrices(M))
    True
    >>> np.allclose(np.dot(M, M.T), concatenate_matrices(M, M.T))
    True

    """
    output = np.identity(4)
    for i in matrices:
        output = np.dot(output, i)
    return output


def inverse_matrix(matrix):
    """Return inverse of square transformation matrix.

    >>> M0 = np.identity(4)
    >>> M1 = inverse_matrix(M0.T)
    >>> np.allclose(M1, np.linalg.inv(M0.T))
    True
    >>> for size in range(1, 7):
    ...     M0 = np.random.rand(size, size)
    ...     M1 = inverse_matrix(M0)
    ...     if not np.allclose(M1, np.linalg.inv(M0)): print(size)

    """
    return np.linalg.inv(matrix)


def apply_transform(vectors, tmatrix):
    """

    Parameters
    ----------
    vectors: list or numpy.array
        array of 3d vectors to transform numpy.array((N,3))
    tmatrix: numpy.array
        transfromation matrix numpy.array((4,4))

    Returns
    -------
    vectors: numpy.array
        numpy.array((N,3))

    Examples
    --------
    >>> tmatrix = np.identity(4)
    >>> apply_transform([[1,2,3], [4,5,6]], tmatrix)
    array([[ 1.,  2.,  3.],
           [ 4.,  5.,  6.]])

    >>> tmatrix[:3, 3] = [1, 1, 1]
    >>> apply_transform([[1,2,3], [4,5,6]], tmatrix)
    array([[ 2.,  3.,  4.],
           [ 5.,  6.,  7.]])

    """
    vectors = np.asarray(vectors, dtype=np.float64)
    vs = np.ones((vectors.shape[0], 4))
    vs[:, :3] = vectors
    return np.einsum('...jk,...k->...j', tmatrix, vs)[:, :3]


def rotate_vectors(vector, axis, theta):
    """rotate the vector v clockwise about the given axis vector
    by theta degrees.

    e.g. rotate([0,1,0],[0,0,1],90) -> [1,0,0]

    Parameters
    ----------
    vector : iterable or list of iterables
        vector to rotate [x,y,z] or [[x1,y1,z1],[x2,y2,z2]]
    axis : iterable
        axis to rotate around [x0,y0,z0]
    theta : float
        rotation angle in degrees
    """
    theta = -1 * theta

    axis = numpy.asarray(axis)
    theta = numpy.asarray(theta) * numpy.pi / 180.
    axis = axis / math.sqrt(numpy.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    rot_matrix = numpy.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                                   [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                                   [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    return numpy.array(numpy.einsum('ij,...j->...i', rot_matrix, vector), ndmin=2)


def angle_between_vectors(v0, v1, directed=True, axis=0):
    """Return angle between vectors.

    If directed is False, the input vectors are interpreted as undirected axes,
    i.e. the maximum angle is pi/2.

    >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3])
    >>> numpy.allclose(a, math.pi)
    True
    >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3], directed=False)
    >>> numpy.allclose(a, 0)
    True
    >>> v0 = [[2, 0, 0, 2], [0, 2, 0, 2], [0, 0, 2, 2]]
    >>> v1 = [[3], [0], [0]]
    >>> a = angle_between_vectors(v0, v1)
    >>> numpy.allclose(a, [0, 1.5708, 1.5708, 0.95532])
    True
    >>> v0 = [[2, 0, 0], [2, 0, 0], [0, 2, 0], [2, 0, 0]]
    >>> v1 = [[0, 3, 0], [0, 0, 3], [0, 0, 3], [3, 3, 3]]
    >>> a = angle_between_vectors(v0, v1, axis=1)
    >>> numpy.allclose(a, [1.5708, 1.5708, 1.5708, 0.95532])
    True

    """
    v0 = numpy.array(v0, dtype=numpy.float64, copy=False)
    v1 = numpy.array(v1, dtype=numpy.float64, copy=False)
    dot = numpy.sum(v0 * v1, axis=axis)
    dot /= np.linalg.norm(v0, axis=axis) * np.linalg.norm(v1, axis=axis)
    return numpy.arccos(dot if directed else numpy.fabs(dot))


def transform_to_crystal(coords, a, b, c, origin=(0, 0, 0)):
    r""" transform from cartesian to crystal fractional coordinates

    Properties
    ------------
    coords : numpy.array((N,3))
    a : numpy.array(3)
    b : numpy.array(3)
    c : numpy.array(3)
    origin : numpy.array(3)

    Notes
    -----
    From https://en.wikipedia.org/wiki/Fractional_coordinates

    .. math::

        \begin{bmatrix}x_{frac}\\y_{frac}\\z_{frac}\\\end{bmatrix}=
        \begin{bmatrix}{
        \frac {1}{a}}&-{\frac {\cos(\gamma )}{a\sin(\gamma )}}&{\frac {\cos(\alpha )\cos(\gamma )-\cos(\beta )}{av\sin(\gamma )}}\\
        0&{\frac {1}{b\sin(\gamma )}}&{\frac {\cos(\beta )\cos(\gamma )-\cos(\alpha )}{bv\sin(\gamma )}}\\
        0&0&{\frac {\sin(\gamma )}{cv}}\\\end{bmatrix}
        \begin{bmatrix}x\\y\\z\\\end{bmatrix}

    such that v is the volume of a unit parallelepiped defined as:

    .. math::

        v={\sqrt {1-\cos ^{2}(\alpha )-\cos ^{2}(\beta )-\cos ^{2}(\gamma )+2\cos(\alpha )\cos(\beta )\cos(\gamma )}}

    """
    # move to origin
    coords = numpy.asarray(coords) - numpy.asarray(origin)

    # create transform matrix
    a_norm = numpy.linalg.norm(a)
    b_norm = numpy.linalg.norm(b)
    c_norm = numpy.linalg.norm(c)

    alpha = angle_between_vectors(b, c)
    beta = angle_between_vectors(a, c)
    gamma = angle_between_vectors(a, b)

    if alpha == 0 or beta == 0 or gamma == 0:
        raise ValueError('a,b,c do not form a basis')

    sin, cos = math.sin, math.cos
    cos_a = cos(alpha)
    cos_b = cos(beta)
    cos_g = cos(gamma)
    sin_g = sin(gamma)

    v = math.sqrt(1 - cos_a ** 2 - cos_b ** 2 - cos_g ** 2 + 2 * cos_a * cos_b * cos_g)

    conv_matrix = numpy.array([
        [1 / a_norm, -(cos_g / (a_norm * sin_g)), (cos_a * cos_g - cos_b) / (a_norm * v * sin_g)],
        [0, 1 / (b_norm * sin_g), (cos_b * cos_g - cos_a) / (b_norm * v * sin_g)],
        [0, 0, sin_g / (c_norm * v)]])

    # transform
    new_coords = numpy.dot(conv_matrix, coords.T).T

    return new_coords


def transform_from_crytal(coords, a, b, c, origin=(0, 0, 0)):
    r""" transform from crystal fractional coordinates to cartesian

    Properties
    ------------
    coords : numpy.array((N,3))

    a : numpy.array(3)

    b : numpy.array(3)

    c : numpy.array(3)

    origin : numpy.array(3)

    Notes
    -----
    From https://en.wikipedia.org/wiki/Fractional_coordinates

    .. math::

        \begin{bmatrix}x\\y\\z\\\end{bmatrix}=
        \begin{bmatrix}a&b\cos(\gamma )&c\cos(\beta )\\0&b\sin(\gamma )&c{\frac {\cos(\alpha )-\cos(\beta )\cos(\gamma )}{\sin(\gamma )}}\\0&0&c{\frac {v}{\sin(\gamma )}}\\\end{bmatrix}
        \begin{bmatrix}x_{frac}\\y_{frac}\\z_{frac}\\\end{bmatrix}

    such that v is the volume of a unit parallelepiped defined as:

    .. math::

        v={\sqrt {1-\cos ^{2}(\alpha )-\cos ^{2}(\beta )-\cos ^{2}(\gamma )+2\cos(\alpha )\cos(\beta )\cos(\gamma )}}

    """
    coords = numpy.asarray(coords)

    # create transform matrix
    a_norm = numpy.linalg.norm(a)
    b_norm = numpy.linalg.norm(b)
    c_norm = numpy.linalg.norm(c)

    alpha = angle_between_vectors(b, c)
    beta = angle_between_vectors(a, c)
    gamma = angle_between_vectors(a, b)

    if alpha == 0 or beta == 0 or gamma == 0:
        raise ValueError('a,b,c do not form a basis')

    sin, cos = math.sin, math.cos
    cos_a = cos(alpha)
    cos_b = cos(beta)
    cos_g = cos(gamma)
    sin_g = sin(gamma)

    v = math.sqrt(1 - cos_a ** 2 - cos_b ** 2 - cos_g ** 2 + 2 * cos_a * cos_b * cos_g)

    conv_matrix = numpy.array([
        [a_norm, b_norm * cos_g, c_norm * cos_b],
        [0, b_norm * sin_g, c_norm * (cos_a - cos_b * cos_a) / sin_g],
        [0, 0, c_norm * v / sin_g]])

    # transform
    new_coords = numpy.dot(conv_matrix, coords.T).T

    # move relative to origin
    coords = numpy.asarray(coords) + numpy.asarray(origin)

    return new_coords

