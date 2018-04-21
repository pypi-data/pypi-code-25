# from https://github.com/BebeSparkelSparkel/MinimumBoundingBox/blob/master/MinimumBoundingBox.py
# important functions: minimum_bounding_box

from scipy.spatial import ConvexHull
from math import sqrt
import numpy as np
from math import atan2, cos, sin, pi
from collections import namedtuple


def unit_vector(pt0, pt1):
    """  returns an unit vector that points in the direction of pt0 to pt1

    Parameters
    ----------
    pt0
    pt1

    Returns
    -------

    """
    dis_0_to_1 = sqrt((pt0[0] - pt1[0]) ** 2 + (pt0[1] - pt1[1]) ** 2)
    return (pt1[0] - pt0[0]) / dis_0_to_1, \
           (pt1[1] - pt0[1]) / dis_0_to_1


def orthogonal_vector(vector):
    """from vector returns a orthogonal/perpendicular vector of equal length
    """
    return -1 * vector[1], vector[0]


def bounding_area(index, hull):
    unit_vector_p = unit_vector(hull[index], hull[index + 1])
    unit_vector_o = orthogonal_vector(unit_vector_p)

    dis_p = tuple(np.dot(unit_vector_p, pt) for pt in hull)
    dis_o = tuple(np.dot(unit_vector_o, pt) for pt in hull)

    min_p = min(dis_p)
    min_o = min(dis_o)
    len_p = max(dis_p) - min_p
    len_o = max(dis_o) - min_o

    return {'area': len_p * len_o,
            'length_parallel': len_p,
            'length_orthogonal': len_o,
            'rectangle_center': (min_p + len_p / 2, min_o + len_o / 2),
            'unit_vector': unit_vector_p,
            }


def to_xy_coordinates(unit_vector_angle, point):
    """returns converted unit vector coordinates in x, y coordinates
    """
    angle_orthogonal = unit_vector_angle + pi / 2
    return point[0] * cos(unit_vector_angle) + point[1] * cos(angle_orthogonal), \
           point[0] * sin(unit_vector_angle) + point[1] * sin(angle_orthogonal)


def rotate_points(center_of_rotation, angle, points):
    """ rotates a point cloud around the center_of_rotation point by angle

    Parameters
    ----------
    center_of_rotation: np.array((2,))
    angle: float
        in radians
    points: list of tuples

    Returns
    -------

    """
    rot_points = []
    ang = []
    for pt in points:
        diff = tuple([pt[d] - center_of_rotation[d] for d in range(2)])
        diff_angle = atan2(diff[1], diff[0]) + angle
        ang.append(diff_angle)
        diff_length = sqrt(sum([d ** 2 for d in diff]))
        rot_points.append((center_of_rotation[0] + diff_length * cos(diff_angle),
                           center_of_rotation[1] + diff_length * sin(diff_angle)))

    return rot_points


def rectangle_corners(rectangle):
    """ returns the corner locations of the bounding rectangle

    Parameters
    ----------
    rectangle: collection.namedtuple
        the output of min_bounding_rectangle

    Returns
    -------

    """
    corner_points = []
    for i1 in (.5, -.5):
        for i2 in (i1, -1 * i1):
            corner_points.append((rectangle['rectangle_center'][0] + i1 * rectangle['length_parallel'],
                                  rectangle['rectangle_center'][1] + i2 * rectangle['length_orthogonal']))

    return rotate_points(rectangle['rectangle_center'], rectangle['unit_vector_angle'], corner_points)


_BoundingBox = namedtuple('BoundingBox', ('area',
                                          'length_parallel',
                                          'length_orthogonal',
                                          'rectangle_center',
                                          'unit_vector',
                                          'unit_vector_angle',
                                          'corner_points'
                                          )
                          )


def minimum_bounding_box(points):
    """ find the listed properties of the minimum bounding box of a point cloud
    
    Parameters
    ----------
    points: list
        points to be a list or tuple of 2D points. ex: ((5, 2), (3, 4), (6, 8)), needs to be more than 2 points

    Returns
    -------
    bounding_box: collections.namedtuple
        contains:
            area: area of the rectangle
            length_parallel: length of the side that is parallel to unit_vector
            length_orthogonal: length of the side that is orthogonal to unit_vector
            rectangle_center: coordinates of the rectangle center
              (use rectangle_corners to get the corner points of the rectangle)
            unit_vector: direction of the length_parallel side. RADIANS
              (it's orthogonal vector can be found with the orthogonal_vector function
            unit_vector_angle: angle of the unit vector
            corner_points: set that contains the corners of the rectangle
    
    Examples
    --------
    >>> bb = minimum_bounding_box(((0,0),(3,0),(1,1)))
    >>> np.allclose(bb.area, 3)
    True
    >>> np.allclose(bb.length_parallel, 3)
    True
    >>> np.allclose(bb.length_orthogonal, 1)
    True
    >>> np.allclose(bb.rectangle_center, (1.5,.5))
    True
    >>> np.allclose(bb.unit_vector, (1,0))
    True
    >>> np.allclose(bb.unit_vector_angle, 0)
    True
    >>> np.allclose(sorted(bb.corner_points), sorted([(0,0),(3,0),(3,1),(0,1)]))
    True

    >>> bb = minimum_bounding_box(((0,0),(0,2),(-1,0),(-.9, 1)))
    >>> np.allclose(bb.area, 2)
    True
    >>> np.allclose(bb.length_parallel, 1)
    True
    >>> np.allclose(bb.length_orthogonal, 2)
    True
    >>> np.allclose(bb.rectangle_center, (-0.5, 1))
    True
    >>> np.allclose(bb.unit_vector, (1,0))
    True
    >>> np.allclose(bb.unit_vector_angle, 0)
    True
    >>> np.allclose(sorted(bb.corner_points), sorted([(0,0),(0,2),(-1,2),(-1,0)]))
    True

    >>> bb = minimum_bounding_box(((0,0),(2,0),(1,1),(3, 1)))
    >>> np.allclose(sorted(bb.corner_points), sorted([(0.0, 0.), (3.0, 0.0), (0.0, 1.0), (3.0, 1.0)]))
    True


    """
    if len(points) <= 2:
        raise ValueError('More than two points required.')

    hull_ordered = [points[index] for index in ConvexHull(points).vertices]
    hull_ordered.append(hull_ordered[0])
    hull_ordered = tuple(hull_ordered)

    min_rectangle = bounding_area(0, hull_ordered)
    for i in range(1, len(hull_ordered) - 1):
        rectangle = bounding_area(i, hull_ordered)
        if rectangle['area'] < min_rectangle['area']:
            min_rectangle = rectangle

    min_rectangle['unit_vector_angle'] = atan2(min_rectangle['unit_vector'][1], min_rectangle['unit_vector'][0])
    min_rectangle['rectangle_center'] = to_xy_coordinates(min_rectangle['unit_vector_angle'],
                                                          min_rectangle['rectangle_center'])

    # this is ugly but a quick hack and is being changed in the speedup branch
    return _BoundingBox(
        area=min_rectangle['area'],
        length_parallel=min_rectangle['length_parallel'],
        length_orthogonal=min_rectangle['length_orthogonal'],
        rectangle_center=min_rectangle['rectangle_center'],
        unit_vector=min_rectangle['unit_vector'],
        unit_vector_angle=min_rectangle['unit_vector_angle'],
        corner_points=list(set(rectangle_corners(min_rectangle)))
    )
