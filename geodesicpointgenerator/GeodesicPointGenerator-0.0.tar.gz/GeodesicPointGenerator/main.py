import numpy as np
import itertools
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

class Generator(object):
    def __init__(self, depth=1, radius=2, center=(0.0, 0.0, 0.0)):

        self._init_depth = depth
        self._sphere_radius = radius
        self._sphere_center = center

        self.points = []
        self.angles = []
        self.__initialize_sphere()

    def plot(self):
        xdata = self.points[:,0]
        ydata = self.points[:,1]
        zdata = self.points[:,2]
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.scatter3D(xdata, ydata, zdata, c=zdata, cmap='Greens')
        plt.show()

    def get_cartesian_coords(self, r, azimuth, elevation):
        x = r * np.sin(elevation) * np.cos(azimuth)
        y = r * np.sin(elevation) * np.sin(azimuth)
        z = r * np.cos(elevation)

        return np.array([x, y, z])

    def __get_unit_vector(self, vector):
        return vector / np.linalg.norm(vector)

    def __get_angle_between_vectors(self, v1, v2):
        v1_u = self.__get_unit_vector(v1)
        v2_u = self.__get_unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    def __set_neighbor_angle_stats(self):
        self.min_angle = np.min(self.angles)
        self.max_angle = np.max(self.angles)
        self.mean_angle = np.mean(self.angles)

    def __subdivide(self, v1, v2, v3, depth):
        if depth == 0:
            self.points.append(v1)
            self.points.append(v2)
            self.points.append(v3)

            # Store min angles
            # ---------------------------------------------
            v1v2 = self.__get_angle_between_vectors(v1, v2)
            v1v3 = self.__get_angle_between_vectors(v1, v3)
            v2v3 = self.__get_angle_between_vectors(v2, v3)

            self.angles.append(v1v2)
            self.angles.append(v1v3)
            self.angles.append(v2v3)
            # ---------------------------------------------

        else:
            v12 = (np.array(v1) + np.array(v2)) / np.linalg.norm(v1 + v2)
            v23 = (np.array(v2) + np.array(v3)) / np.linalg.norm(v2 + v3)
            v31 = (np.array(v3) + np.array(v1)) / np.linalg.norm(v3 + v1)

            self.__subdivide(v1, v12, v31, depth-1)
            self.__subdivide(v2, v23, v12, depth-1)
            self.__subdivide(v3, v31, v23, depth-1)
            self.__subdivide(v12, v23, v31, depth-1)

    def __transform_points(self):
        # Transform
        transformed_points = []
        for points in self.points:
            point_transform = np.array(points) * self._sphere_radius + self._sphere_center
            transformed_points.append(point_transform)

        self.points = np.array(transformed_points)

    def __convert_to_spherical_coords(self):
        self.spherical_points = []
        for x, y, z in self.points:
            r = np.sqrt(x**2 + y**2 + z**2)
            self.spherical_points.append({
                "r"             : r,
                "elevation"     : np.arccos( z / (r+1e-9) ),
                "azimuth"       : np.arctan2( y, (x+1e-9) )
            })

    def __initialize_sphere(self):
        X = 0.525731112119133606
        Z = 0.850650808352039932

        vdata = [
            [-X, 0.0, Z], [X, 0.0, Z],   [-X, 0.0, -Z],  [X, 0.0, -Z],
            [0.0, Z, X],  [0.0, Z, -X],  [0.0, -Z, X],   [0.0, -Z, -X],
            [Z, X, 0.0],  [-Z, X, 0.0],  [Z, -X, 0.0],   [-Z, -X, 0.0]
        ]

        vertex_indices = [
            [0, 4, 1],  [0, 9, 4],  [9, 5, 4],  [4, 5, 8],  [4, 8, 1],
            [8, 10, 1], [8, 3, 10], [5, 3, 8],  [5, 2, 3],  [2, 7, 3],
            [7, 10, 3], [7, 6, 10], [7, 11, 6], [11, 0, 6], [0, 1, 6],
            [6, 1, 10], [9, 0, 11], [9, 11, 2], [9, 2, 5],  [7, 2, 11]
        ]

        for vertex_i in vertex_indices:
            v1, v2, v3 = vertex_i
            self.__subdivide(vdata[v1], vdata[v2], vdata[v3], self._init_depth)

        self.__transform_points()
        self.__set_neighbor_angle_stats()
        self.__convert_to_spherical_coords()
