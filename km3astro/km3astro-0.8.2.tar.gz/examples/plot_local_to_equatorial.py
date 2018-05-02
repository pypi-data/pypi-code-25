"""
===============================
Local to Equatorial Coordinates
===============================

Where do my neutrinos come from?
"""

__author__ = 'moritz'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from km3astro.coord import local_event, get_location
from km3astro.plot import plot_equatorial
from km3pipe.math import neutrino_to_source_direction
import km3pipe.style.default   # noqa


##########################################################
# Detector Coordinates
# --------------------
# Let's define some random events.

theta = np.array([10, 45, 70, 23, 20, 11, 24, 54]) * np.pi / 180
phi = np.array([4, 23, 200, 320, 10, 45, 29, 140]) * np.pi / 180
time = pd.to_datetime([
    '2015-01-12T15:10:12',
    '2015-06-12T13:48:56',
    '2015-03-09T21:57:52',
    '2015-03-15T14:24:01',
    '2015-01-12T15:10:12',
    '2015-06-12T13:48:56',
    '2015-03-09T21:57:52',
    '2015-03-15T14:24:01',
]).values

print(theta[:3])
print(phi[:3])
print(time[:3])

##########################################################
# Phi, theta: Where the neutrino is pointing to
#
# Zenith, azimuth: where the neutrino is coming from

azimuth, zenith = neutrino_to_source_direction(phi, theta, radian=True)

print(azimuth[:3])
print(zenith[:3])

#########################################################################
# We want to observe them from the Orca location. Let's look at our
# geographical coordinates.
#
# In km3astro, there are the predefined locations "orca", "arca" and "antares".
orca_loc = get_location('orca')
print(
    orca_loc.lon.degree,
    orca_loc.lat.degree
)

#########################################################################
# Create event in local coordinates (aka AltAz or Horizontal Coordinates)
#
# This returns an ``astropy.SkyCoord`` instance.

evt_local = local_event(
    azimuth=azimuth, zenith=zenith, time=time,
    location='orca'
)

print(evt_local)

##############################################################
# Transform to equatorial -- ICRS
# -------------------------------
#
# "If you’re looking for “J2000” coordinates, and aren’t sure if
# you want to use this or FK5, you probably want to use ICRS. It’s more
# well-defined as a catalog coordinate and is an inertial system, and is
# very close (within tens of milliarcseconds) to J2000 equatorial."

evt_equat = evt_local.transform_to('icrs')
print(evt_equat)

##############################################################
# Plot them in a square

right_ascension_radian = evt_equat.ra.rad
declination_radian = evt_equat.dec.rad

plt.scatter(right_ascension_radian, declination_radian)
plt.xlabel('Right Ascension / rad')
plt.ylabel('Declination / rad')

##############################################################
# Plot them in a skymap.
#
# We need this little wrap because astropy's
# convention for ra, dec differs from matplotlib.
plot_equatorial(evt_equat, markersize=12)
