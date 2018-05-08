# -*- coding: utf-8 -*-

import math
import numpy as np
from .tidegravity import calculate_julian_century


def lunar_mean_longitude(time):
    T, t0 = calculate_julian_century(np.array([time]))
    T2 = T ** 2
    T3 = T ** 3
    s = 4.72000889397 + 8399.70927456 * T + 3.45575191895e-05 * T2 + 3.49065850399e-08 * T3

    print("s: ", math.degrees(s % (2 * math.pi)))

    # (N) Longitude of the moon's ascending node in its orbit reckoned from the referred equinox
    N = 4.52360161181 - 33.757146295 * T + 3.6264063347e-05 * T2 + 3.39369576777e-08 * T3
    print("N (rads):", N)
    print("N (deg): ", math.degrees(N % (math.pi * 2)))
    cosN = np.cos(N)
    sinN = np.sin(N)

    i = 0.08979719  # (i) Inclination of the moon's orbit to the ecliptic
    ω = math.radians(23.452)  # Inclination of the Earth's equator to the ecliptic
    # I (uppercase i) Inclination of the moon's orbit to the equator
    I = np.arccos(np.cos(ω) * np.cos(i) - np.sin(ω) * np.sin(i) * cosN)
    # ν (nu) Longitude in the celestial equator of its intersection A with the moon's orbit
    ν = np.arcsin(np.sin(i) * sinN / np.sin(I))
    print('v: ', ν)

    # cos α (alpha) where α is defined in eq. 15 and 16
    cos_α = cosN * np.cos(ν) + sinN * np.sin(ν) * np.cos(ω)
    # sin α (alpha) where α is defined in eq. 15 and 16
    sin_α = math.sin(ω) * sinN / np.sin(I)
    # (α) α is defined in eq. 15 and 16
    α = 2 * np.arctan(sin_α / (1 + cos_α))
    # ξ (xi) Longitude in the moon's orbit of its ascending intersection with the celestial equator
    ξ = N - α
    print("xi: ", ξ[0])
    print("xi(deg): ", math.degrees(ξ[0] % (math.pi * 2)))

    # σ (sigma) Mean longitude of moon in radians in its orbit reckoned from A
    σ = s - ξ
    print('sigma(rads): ', σ)
    print('sigma(deg):', math.degrees(σ % (math.pi * 2)))
    # l (lowercase el) Longitude of moon in its orbit reckoned from its ascending intersection with the equator
    # l = σ + 2 * e * np.sin(s - p) + (5. / 4) * e * e * np.sin(2 * (s - p)) + (15. / 4) * m * e * np.sin(s - 2 * h + p) \
    #     + (11. / 8) * m * m * np.sin(2 * (s - h))

