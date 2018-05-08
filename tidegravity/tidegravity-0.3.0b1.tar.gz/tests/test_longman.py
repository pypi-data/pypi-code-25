# -*- coding: utf-8 -*-

from datetime import datetime
import numpy as np
import pytest

from tidegravity import solve_longman_tide, solve_longman_tide_scalar, solve_tide_df, solve_point_corr
from tidegravity import import_trajectory, calculate_julian_century


def test_array_calculation():
    lat = np.array([47.1234, 49.8901])
    lon = np.array([104.9903, 105.9901])
    alt = np.array([1609.3, 1700.1])
    time = np.array([datetime(2018, 4, 17, 12, 0, 0),
                     datetime(2018, 4, 17, 13, 0, 0)])

    lunar, solar, total = solve_longman_tide(lat, lon, alt, time)
    assert 2 == len(lunar) == len(solar) == len(total)


def test_static_location_tide():
    lat = np.array([40.7914])
    lon = np.array([282.1414])
    alt = np.array([370.])
    time = np.array([datetime(2015, 4, 23, 0, 0, 0)])

    gm, gs, g = solve_longman_tide(lat, lon, alt, time)
    assert gm[0] == pytest.approx(0.0324029651226)
    assert gs[0] == pytest.approx(-0.0288682178454)
    assert g[0] == pytest.approx(0.00353474727722)


def test_solve_point_corr():
    # Test solving tide over a period given static lat/lon/alt
    lat = 39.7392
    lon = -104.9903
    alt = 1609.3
    t0 = datetime(2018, 4, 18, 12, 0, 0)

    res = solve_point_corr(lat, lon, alt, t0, n=10000, increment='S')


def test_solve_trajectory_input():
    file = 'tests/test_gps_data.txt'

    trajectory = import_trajectory(file, timeformat='hms')

    df = solve_tide_df(trajectory, lat='lat', lon='long', alt='ell_ht')
    assert len(df) == len(trajectory)


def test_compare_matlab_synthetic(matlab_df):
    calculated_df = solve_tide_df(matlab_df.copy(), lat='lat', lon='lon', alt='alt')
    # Drop gravity component columns for comparison with MATLAB
    calculated_df = calculated_df.drop(['gm', 'gs'], axis=1)

    assert np.allclose(matlab_df, calculated_df, atol=1e-3)
    assert np.allclose(calculated_df, matlab_df, atol=1e-3)


def test_solve_longman_scalar():
    lat = 40.7914
    lon = 282.1414
    alt = 370.
    time = datetime(2015, 4, 23, 0, 0, 0)

    gm, gs, g0 = solve_longman_tide_scalar(lat, lon, alt, time)
    assert gm == pytest.approx(0.0324029651226)
    assert gs == pytest.approx(-0.0288682178454)
    assert g0 == pytest.approx(0.00353474727722)
