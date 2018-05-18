import math

class Pose:
    """
    Represent the x, y, theta pose of an object in 2D space
    """
    x = 0.0
    y = 0.0
    theta = 0.0
    def __init__(self, x, y, theta):
        self.x = x
        """x coordinate"""
        self.y = y
        """y coordinate"""
        self.theta = theta
        """rotation in radians"""

    def point(self):
        """
        Return just the x, y parts represented as a ``util.Point``
        """
        return Point(self.x, self.y)

    def transform(self):
        """
        Return a transformation matrix that corresponds to rotating by theta 
        and then translating by x,y (in the original coordinate frame).
        """
        cos_th = math.cos(self.theta)
        sin_th = math.sin(self.theta)
        return Transform([[cos_th, -sin_th, self.x],
                          [sin_th, cos_th, self.y],
                          [0, 0, 1]])

    def transform_point(self, point):
        """
        Applies the pose.transform to point and returns new point.
        :param point: an instance of ``util.Point``
        """
        cos_th = math.cos(self.theta)
        sin_th = math.sin(self.theta)
        return Point(self.x + cos_th * point.x - sin_th * point.y,
                     self.y + sin_th * point.x + cos_th * point.y)

    def transform_delta(self, point):
        """
        Does the rotation by theta of the pose but does not add the
        x,y offset. This is useful in transforming the difference(delta)
        between two points.
        :param point: an instance of ``util.Point``
        :returns: a ``util.Point``.
        """
        cos_th = math.cos(self.theta)
        sin_th = math.sin(self.theta)
        return Point(cos_th * point.x - sin_th * point.y,
                     sin_th * point.x + cos_th * point.y)

    def transform_pose(self, pose):
        """
        Make self into a transformation matrix and apply it to pose.
        :returns: Af new ``util.pose``.
        """
        return self.transform().apply_to_pose(pose)

    def near(self, pose, dist_eps, angle_eps):
        """
        :returns: True if pose is within dist_eps and angle_eps of self
        """
        return self.point().is_near(pose.point(), dist_eps) and \
               near_angle(self.theta, pose.theta, angle_eps)

    def diff(self, pose):
        """
        :param pose: an instance of ``util.Pose``
        :returns: a pose that is the difference between self and pose (in
         x, y, and theta)
        """
        return Pose(self.x-pose.x,
                    self.y-pose.y,
                    fix_angle_plus_minus_pi(self.theta-pose.theta))

    def distance(self, pose):
        """
        :param pose: an instance of ``util.Pose``
        :returns: the distance between the x,y part of self and the x,y
         part of pose.
        """
        return self.point().distance(pose.point())

    def inverse(self):
        """
        Return a pose corresponding to the transformation matrix that
        is the inverse of the transform associated with this pose.  If this
        pose's transformation maps points from frame X to frame Y, the inverse
        maps points from frame Y to frame X.
        """
        return self.transform().inverse().pose()

    def xyt_tuple(self):
        """
        :returns: a representation of this pose as a tuple of x, y,
         theta values  
        """
        return (self.x, self.y, self.theta)
    
    def __repr__(self):
        return 'pose:'+ pretty_string(self.xyt_tuple())

def value_list_to_pose(values):
    """
    :param values: a list or tuple of three values: x, y, theta
    :returns: a corresponding ``util.Pose``
    """
    return Pose(*values)

class Point:
    """
    Represent a point with its x, y values
    """
    x = 0.0
    y = 0.0
    def __init__(self, x, y):
        self.x = x
        """x coordinate"""
        self.y = y
        """y coordinate"""

    def is_near(self, point, dist_eps):
        """
        :param point: instance of ``util.Point``
        :param dist_eps: positive real number
        :returns: true if the distance between ``self`` and ``util.Point`` is less
         than dist_eps
        """
        return self.distance(point) < dist_eps

    def distance(self, point):
        """
        :param point: instance of ``util.Point``
        :returns: Euclidean distance between ``self`` and ``util.Point``
         than dist_eps
        """
        return math.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

    def magnitude(self):
        """
        :returns: Magnitude of this point, interpreted as a vector in
         2-space 
        """
        return math.sqrt(self.x**2 + self.y**2)

    def xyTuple(self):
        """
        :returns: pair of x, y values
        """
        return (self.x, self.y)

    def __repr__(self):
        return 'point:'+ pretty_string(self.xyTuple())

    def angleTo(self, p):
        """
        :param p: instance of ``util.Point`` or ``util.Pose``
        :returns: angle in radians of vector from self to p
        """
        dx = p.x - self.x
        dy = p.y - self.y
        return math.atan2(dy, dx)

    def add(self, point):
        """
        Vector addition
        """
        return Point(self.x + point.x, self.y + point.y)
    def __add__(self, point):
        return self.add(point)
    def sub(self, point):
        """
        Vector subtraction
        """
        return Point(self.x - point.x, self.y - point.y)
    def __sub__(self, point):
        return self.sub(point)
    def scale(self, s):
        """
        Vector scaling
        """
        return Point(self.x*s, self.y*s)
    def __rmul__(self, s):
        return self.scale(s)
    def dot(self, p):
        """
        Dot product
        """
        return self.x*p.x + self.y*p.y

class Transform:
    """
    Rotation and translation represented as 3 x 3 matrix
    """
    def __init__(self, matrix = None):
        if matrix == None:
            self.matrix = make_2d_array(3, 3, 0)
            """matrix representation of transform"""
        else:
            self.matrix = matrix

    def inverse(self):
        """
        Returns transformation matrix that is the inverse of this one
        """
        ((c, ms, x),(s, c2, y), (z1, z2, o)) = self.matrix
        return Transform([[c, s, (-c*x)-(s*y)],
                          [-s, c, (s*x)-(c*y)],
                          [0, 0, 1]])

    def compose(self, trans):
        """
        Returns composition of self and trans
        """
        return Transform(mm(self.matrix, trans.matrix))

    def pose(self):
        """
        Convert to Pose
        """
        theta = math.atan2(self.matrix[1][0], self.matrix[0][0])
        return Pose(self.matrix[0][2], self.matrix[1][2], theta)

    def apply_to_point(self, point):
        """
        Transform a point into a new point.
        """
        # could convert the point to a vector and do multiply instead
        return self.pose().transform_point(point)

    def apply_to_pose(self, pose):
        """
        Transform a pose into a new pose.
        """
        return self.compose(pose.transform()).pose()

    def __repr__(self):
        return 'transform:'+ pretty_string(self.matrix)

def near_angle(a1, a2, eps):
    """
    :param a1: number representing angle; no restriction on range
    :param a2: number representing angle; no restriction on range
    :param eps: positive number
    :returns: ``True`` if ``a1`` is within ``eps`` of ``a2``.  Don't use
     within for this, because angles wrap around!
    """
    return abs(fix_angle_plus_minus_pi(a1-a2)) < eps

def mm(t1, t2):
    """
    Multiplies 3 x 3 matrices represented as lists of lists
    """
    result = make_2d_array(3, 3, 0)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                result[i][j] += t1[i][k]*t2[k][j]
    return result

def fix_angle_plus_minus_pi(a):
    """
    A is an angle in radians;  return an equivalent angle between plus
    and minus pi
    """
    return ((a+math.pi)%(2*math.pi))-math.pi

def make_2d_array(dim1, dim2, init_value):
    """
    Return a list of lists representing a 2D array with dimensions
    dim1 and dim2, filled with initialValue
    """
    result = []
    for i in range(dim1):
        result = result + [make_vector(dim2, init_value)]
    return result

def make_2d_array_fill(dim1, dim2, init_fun):
    """
    Return a list of lists representing a 2D array with dimensions
    dim1 and dim2, filled by calling init_fun with every pair of
    indices 
    """
    result = []
    for i in range(dim1):
        result = result + [make_vector_fill(dim2, lambda j: init_fun(i, j))]
    return result

def make_3d_array(dim1, dim2, dim3, init_value):
    """
    Return a list of lists of lists representing a 3D array with dimensions
    dim1, dim2, and dim3 filled with initialValue
    """
    result = []
    for i in range(dim1):
        result = result + [make_2d_array(dim2, dim3, init_value)]
    return result

def map_array_3d(array, f):
    """
    Map a function over the whole array.  Side effects the array.  No
    return value.
    """
    for i in range(len(array)):
        for j in range(len(array[0])):
            for k in range(len(array[0][0])):
                array[i][j][k] = f(array[i][j][k])

def make_vector(dim, init_value):
    """
    Return a list of dim copies of init_value
    """
    return [init_value]*dim

def make_vector_fill(dim, init_fun):
    """
    Return a list resulting from applying init_fun to values from 0 to
    dim-1
    """
    return [init_fun(i) for i in range(dim)]

def pretty_string(struct):
    """
    Make nicer looking strings for printing, mostly by truncating
    floats
    """
    if type(struct) == list:
        return '[' + ', '.join([pretty_string(item) for item in struct]) + ']'
    elif type(struct) == tuple:
        return '(' + ', '.join([pretty_string(item) for item in struct]) + ')'
    elif type(struct) == dict:
        return '{' + ', '.join([str(item) + ':' +  pretty_string(struct[item]) \
                                             for item in struct]) + '}'
    elif type(struct) == float:
        return "%5.6f" % struct
    else:
        return str(struct)
