"""
Test reading and applying ftresults.
"""

from . import DATA_DIR

from sblu import ft


def test_read_ftresults():
    ftresults = ft.read_ftresults(DATA_DIR / "ft/ft.test")

    assert len(ftresults) == 10


def test_read_mol2_rotations():
    rotations = ft.read_rotations(DATA_DIR / "prms/rotation_test_set.mol2")

    assert rotations.shape == (10, 3, 3)


def test_read_mol2_rotations_stream():
    with open(DATA_DIR / "prms/rotation_test_set.mol2") as f:
        rotations = ft.read_rotations_stream(f)

    assert rotations.shape == (10, 3, 3)


def test_read_prm_rotations():
    rotations = ft.read_rotations(DATA_DIR / "prms/rotation_test_set.prm")

    assert rotations.shape == (10, 3, 3)


def test_read_prm_rotations_stream():
    with open(DATA_DIR / "prms/rotation_test_set.prm") as f:
        rotations = ft.read_rotations_stream(f)

    assert rotations.shape == (10, 3, 3)


def test_get_ftresult():
    ftresult = ft.get_ftresult(DATA_DIR / "ft/ft.test", 0)

    assert ftresult['roti'] == 9
    assert (ftresult['tv'] == [1.0, 11.0, -21.0]).all()
    assert ftresult['E'] == -451.6
