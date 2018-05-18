"""
A wide variety of utility procedures and classes.
"""

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

    def is_near(self, pose, dist_eps, angle_eps):
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
        self.x = float(x)
        """x coordinate"""
        self.y = float(y)
        """y coordinate"""

    def near(self, point, dist_eps):
        """
        :param point: instance of ``util.Point``
        :param dist_eps: positive real number
        :returns: true if the distance between ``self`` and ``util.Point`` is less
         than dist_eps
        """
        return self.distance(point) < dist_eps

    # This is hear for backward compatibility
    is_near = near

    def distance(self, point):
        """
        :param point: instance of ``util.Point``
        :returns: Euclidean distance between ``self`` and ``util.Point``
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

class Line:
    """
    Line in 2D space
    """
    def __init__(self, p1, p2):
        """
        Initialize with two points that are on the line.  Actually
        store a normal and an offset from the origin
        """
        self.theta = p1.angleTo(p2)
        """normal angle"""
        self.nx = -math.sin(self.theta)
        """x component of normal vector"""
        self.ny = math.cos(self.theta)
        """y component of normal vector"""
        self.off = p1.x * self.nx + p1.y * self.ny
        """offset along normal"""

    def point_on_line(self, p, eps):
        """
        Return true if p is within eps of the line
        """
        dist = abs(p.x*self.nx + p.y*self.ny - self.off)
        return dist < eps

    def __repr__(self):
        return 'line:'+ pretty_string((self.nx, self.ny, self.off))

class LineSeg:
    """
    Line segment in 2D space
    """
    def __init__(self, p1, p2):
        """
        Initialize with two points that are on the line.  Store one of
        the points and the vector between them.
        """
        self.p1 = p1
        """One point"""
        self.p2 = p2
        """Other point"""
        self.M = p2 - p1
        """Vector from the stored point to the other point"""

    def closest_point(self, p):
        """
        Return the point on the line that is closest to point p
        """
        t0 = self.M.dot(p - self.p1) / self.M.dot(self.M)
        if t0 <= 0:
            return self.p1
        elif t0 >= 1:
            return self.p1 + self.M
        else:
            return self.p1 + t0 * self.M

    def dist_to_point(self, p):
        """
        Shortest distance between point p and this line
        """
        return p.distance(self.closest_point(p))

    def intersection(self, other):
        """
        Return a ``Point`` where ``self`` intersects ``other``.  Returns ``False``
        if there is no intersection.
        :param other: a ``LineSeg``
        """
        def helper(l1, l2):
            (a, b, c, d) = (l1.p1, l1.p2, l2.p1, l2.p2)
            try:
                s = ((b.x-a.x)*(a.y-c.y)+(b.y-a.y)*(c.x-a.x))/\
                    ((b.x-a.x)*(d.y-c.y)-(b.y-a.y)*(d.x-c.x)) 
                t = ((c.x-a.x)+(d.x-c.x)*s)/(b.x-a.x)
                if s <= 1 and s >=0 and t <= 1 and t >= 0:
                    fromt = Point(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t)
                    froms = Point(c.x+(d.x-c.x)*s,c.y+(d.y-c.y)*s)
                    if fromt.near(froms, 0.001):
                        return fromt
                    else:
                        return False 
                else:
                    return False 
            except ZeroDivisionError:
                return False
        first = helper(self, other)
        if first:
            return first
        else:
            return helper(other, self)

    def __repr__(self):
        return 'lineSeg:'+ pretty_string((self.p1, self.p2))

#####################

def local_to_global(pose, point):
    """
    Same as pose.transform_point(point)
    :param point: instance of ``util.Point``
    """
    return pose.transform_point(point)

def local_pose_to_global_pose(pose1, pose2):
    """
    Applies the transform from pose1 to pose2
    :param pose1: instance of ``util.Pose``
    :param pose2: instance of ``util.Pose``
    """
    return pose1.transform().apply_to_pose(pose2)

def inverse_pose(pose):
    """
    Same as pose.inverse()
    :param pose: instance of ``util.Pose``
    """
    return pose.transform().inverse().pose()

# Given robot's pose in a global frame and a point in the global frame
# return coordinates of point in local frame
def global_to_local(pose, point):
    """
    Applies inverse of pose to point.
    :param pose: instance of ``util.Pose``
    :param point: instance of ``util.Point``
    """
    return inverse_pose(pose).transform_point(point)

def global_pose_to_local_pose(pose1, pose2):
    """
    Applies inverse of pose1 to pose2.
    :param pose1: instance of ``util.Pose``
    :param pose2: instance of ``util.Pose``
    """
    return inverse_pose(pose1).transform().apply_to_pose(pose2)

# Given robot's pose in a global frame an a point in the global frame
# return coordinates of point in local frame
def global_delta_to_local(pose, deltaPoint):
    """
    Applies inverse of pose to delta using transform_delta.
    :param pose: instance of ``util.Pose``
    :param deltaPoint: instance of ``util.Point``
    """
    return inverse_pose(pose).transform_delta(deltaPoint)

def sum(items):
    """
    Defined to work on items other than numbers, which is not true for
    the built-in sum.
    """
    if len(items) == 0:
        return 0
    else:
        result = items[0]
        for item in items[1:]:
            result += item
        return result

def within(v1, v2, eps):
    """
    :param v1: number
    :param v2: number
    :param eps: positive number
    :returns: ``True`` if ``v1`` is with ``eps`` of ``v2`` 
    """
    return abs(v1 - v2) < eps

def near_angle(a1, a2, eps):
    """
    :param a1: number representing angle; no restriction on range
    :param a2: number representing angle; no restriction on range
    :param eps: positive number
    :returns: ``True`` if ``a1`` is within ``eps`` of ``a2``.  Don't use
     within for this, because angles wrap around!
    """
    return abs(fix_angle_plus_minus_pi(a1-a2)) < eps

def nearly_equal(x,y):
    """
    Like within, but with the tolerance built in
    """
    return abs(x-y)<.0001

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

def fix_angle_02_pi(a):
    """
    :param a: angle in radians
    :returns: return an equivalent angle between 0 and 2 pi
    """
    return a%(2*math.pi)

def reverse_copy(items):
    """
    Return a list that is a reversed copy of items
    """
    item_copy = items[:]
    item_copy.reverse()
    return item_copy


def dot_prod(a, b):
    """
    Return the dot product of two lists of numbers
    """
    return sum([ai*bi for (ai,bi) in zip(a,b)])

def argmax(l, f):
    """
    :param l: ``List`` of items
    :param f: ``Procedure`` that maps an item into a numeric score
    :returns: the element of ``l`` that has the highest score
    """
    vals = [f(x) for x in l]
    return l[vals.index(max(vals))]

def argmax_with_val(l, f):
    """
    :param l: ``List`` of items
    :param f: ``Procedure`` that maps an item into a numeric score
    :returns: the element of ``l`` that has the highest score and the score
    """
    best = l[0]; best_score = f(best)
    for x in l:
        x_score = f(x)
        if x_score > best_score:
            best, best_score = x, x_score
    return (best, best_score)

def argmax_index(l, f = lambda x: x):
    """
    :param l: ``List`` of items
    :param f: ``Procedure`` that maps an item into a numeric score
    :returns: the index of ``l`` that has the highest score
    """
    best = 0; best_score = f(l[best])
    for i in range(len(l)):
        x_score = f(l[i])
        if x_score > best_score:
            best, best_score = i, x_score
    return (best, best_score)

def argmax_indices_3d(l, f = lambda x: x):
    best = (0,0,0); best_score = f(l[0][0][0])
    for i in range(len(l)):
        for j in range(len(l[0])):
            for k in range(len(l[0][0])):
                x_score = f(l[i][j][k])
                if x_score > best_score:
                    best, best_score = (i, j, k), x_score
    return (best, best_score)

def random_multinomial(dist):
    """
    :param dist: List of positive numbers summing to 1 representing a
     multinomial distribution over integers from 0 to ``len(dist)-1``.
    :returns: random draw from that distribution
    """
    r = random.random()
    for i in range(len(dist)):
        r = r - dist[i]
        if r < 0.0:
            return i
    return "weird"

def clip(v, v_min, v_max):
    """
    :param v: number
    :param v_min: number (may be None, if no limit)
    :param v_max: number greater than ``v_min`` (may be None, if no limit)
    :returns: If ``v_min <= v <= v_max``, then return ``v``; if ``v <
     v_min`` return ``v_min``; else return ``v_max``
    """
    if v_min == None:
        if v_max == None:
            return v
        else:
            return min(v, v_max)
    else:
        if v_max == None:
            return max(v, v_min)
        else:
            return max(min(v, v_max), v_min)

def sign(x):
    """
    Return 1, 0, or -1 depending on the sign of x
    """
    if x > 0.0:
        return 1
    elif x == 0.0:
        return 0
    else:
        return -1

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
    ``dim1`` and ``dim2``, filled by calling ``init_fun(ix, iy)`` with
    ``ix`` ranging from 0 to ``dim1 - 1`` and ``iy`` ranging from 0 to
    ``dim2-1``. 
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
  
def pretty_print(struct):
    s = pretty_string(struct)
    print(s)

class SymbolGenerator:
    """
    Generate new symbols guaranteed to be different from one another
    Optionally, supply a prefix for mnemonic purposes
    Call gensym("foo") to get a symbol like 'foo37'
    """
    def __init__(self):
        self.count = 0
    def gensym(self, prefix = 'i'):
        self.count += 1
        return prefix + '_' + str(self.count)
    
gensym = SymbolGenerator().gensym
"""Call this function to get a new symbol"""

def log_gaussian(x, mu, sigma):
    """
    Log of the value of the gaussian distribution with mean mu and
    stdev sigma at value x
    """
    return -((x-mu)**2 / (2*sigma**2)) - math.log(sigma*math.sqrt(2*math.pi))

def gaussian(x, mu, sigma):
    """
    Value of the gaussian distribution with mean mu and
    stdev sigma at value x
    """
    return math.exp(-((x-mu)**2 / (2*sigma**2))) /(sigma*math.sqrt(2*math.pi))  

def line_indices(cell1, cell2):
    """
    Takes two cells in the grid (each described by a pair of integer
    indices), and returns a list of the cells in the grid that are on the
    line segment between the cells.
    """
    (i0, j0) = cell1
    (i1, j1) = cell2
    assert type(i0) == int, 'Args to line_indices must be pairs of integers'
    assert type(j0) == int, 'Args to line_indices must be pairs of integers'
    assert type(i1) == int, 'Args to line_indices must be pairs of integers'
    assert type(j1) == int, 'Args to line_indices must be pairs of integers'
    
    ans = [(i0,j0)]
    di = i1 - i0
    dj = j1 - j0
    t = 0.5
    if abs(di) > abs(dj):               # slope < 1
        m = float(dj) / float(di)       # compute slope
        t += j0
        if di < 0: di = -1
        else: di = 1
        m *= di
        while (i0 != i1):
            i0 += di
            t += m
            ans.append((i0, int(t)))
    else:
        if dj != 0:                     # slope >= 1
            m = float(di) / float(dj)   # compute slope
            t += i0
            if dj < 0: dj = -1
            else: dj = 1
            m *= dj
            while j0 != j1:
                j0 += dj
                t += m
                ans.append((int(t), j0))
    return ans

def line_indices_conservative(cell1, cell2):
    """
    Takes two cells in the grid (each described by a pair of integer
    indices), and returns a list of the cells in the grid that are on the
    line segment between the cells.  This is a conservative version.
    """
    (i0, j0) = cell1
    (i1, j1) = cell2
    assert type(i0) == int, 'Args to line_indices must be pairs of integers'
    assert type(j0) == int, 'Args to line_indices must be pairs of integers'
    assert type(i1) == int, 'Args to line_indices must be pairs of integers'
    assert type(j1) == int, 'Args to line_indices must be pairs of integers'
    
    ans = [(i0,j0)]
    di = i1 - i0
    dj = j1 - j0
    t = 0.5
    if abs(di) > abs(dj):               # slope < 1
        m = float(dj) / float(di)       # compute slope
        t += j0
        if di < 0: di = -1
        else: di = 1
        m *= di
        while (i0 != i1):
            i0 += di
            t1 = t + m
            if int(t1) == int(t):
                ans.append((i0, int(t1)))
            else:
                ans.append((i0-di, int(t1)))
                ans.append((i0, int(t)))
                ans.append((i0, int(t1)))
            t = t1
    else:
        if dj != 0:                     # slope >= 1
            m = float(di) / float(dj)   # compute slope
            t += i0
            if dj < 0: dj = -1
            else: dj = 1
            m *= dj
            while j0 != j1:
                j0 += dj
                t1 = t + m
                if int(t1) == int(t):
                    ans.append((int(t1), j0))
                else:
                    ans.append((int(t1), j0-dj))
                    ans.append((int(t), j0))
                    ans.append((int(t1), j0))
                t = t1
    return ans

import sys, os
def find_file(filename):
    """
    Takes a filename and returns a complete path to the first instance of the file found within the subdirectories of the brain directory.
    """
    libdir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
    braindir = os.path.abspath(libdir+'/..')
    for (root, dirs, files) in os.walk(braindir):
        for f in files:
            if f == filename:
                return root+'/'+f
    print(("Couldn't find file: ", filename))
    return '.'
# This only works if the brain directory is in sys.path, which isn't 
# true unless we put it there, which is complicated
# def find_file(filename):
#     """
#     Takes a filename and returns the first directory in sys.path that contains
#     the file
#     """
#     for p in sys.path:
#         if os.path.exists(p+'/'+filename):
#             return os.path.abspath(p)+'/'+filename
#     print 'Could not find file: ', filename
#     return filename

