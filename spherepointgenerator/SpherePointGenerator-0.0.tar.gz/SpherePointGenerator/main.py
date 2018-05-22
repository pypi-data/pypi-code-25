import numpy as np
import itertools
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

class Generator(object):
    def __init__(self, num_points=200, radius=1, center=(0.0, 0.0, 0.0)):

        self._desired_num_points = num_points
        self._radius = radius
        self._sphere_center = center

        self.points = []
        self.angles = []
        self.__initialize_sphere()

    def plot(self):
        points = self.points["cartesian"]
        xdata = points[:,0]
        ydata = points[:,1]
        zdata = points[:,2]
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.scatter3D(xdata, ydata, zdata, cmap='Greens')
        plt.show()

    def __create_point(self, theta, phi):
        """
            phi = azimuth
            theta = polar angle (elevation)
        """

        x = self._radius * np.sin(theta) * np.cos(phi)
        y = self._radius * np.sin(theta) * np.sin(phi)
        z = self._radius * np.cos(theta)

        cartesian_points = np.array([x, y, z])
        spherical_points = np.array([self._radius, phi, theta])

        self.points["cartesian"].append(cartesian_points)
        self.points["spherical"].append(spherical_points)

    def __initialize_sphere(self):
        self.num_points = 0
        area = (4 * np.pi * self._radius) / self._desired_num_points
        diameter = np.sqrt(area)
        M_theta = int(np.round(np.pi / diameter))
        d_theta = np.pi / M_theta
        d_phi = area / float(d_theta)

        self.points = {"cartesian" : [], "spherical" : []}

        theta_deltas = []
        prev_theta = None
        for i, m in enumerate(range(M_theta)):
            theta = np.pi*(m + 0.5) / M_theta
            M_phi = int(np.round(2*np.pi*np.sin(theta)/d_theta))

            if prev_theta is not None:
                theta_delta = np.abs(theta - prev_theta)
                theta_deltas.append(theta_delta)

            prev_theta = theta
            for n in range(M_phi):
                phi = 2 * np.pi * n / M_phi
                self.__create_point(theta, phi)

                self.num_points += 1

        self.angle_rad = np.mean(theta_deltas)
        self.angle_deg = np.degrees(self.angle_rad)

        for key, val in self.points.items():
            self.points[key] = np.array(val)
