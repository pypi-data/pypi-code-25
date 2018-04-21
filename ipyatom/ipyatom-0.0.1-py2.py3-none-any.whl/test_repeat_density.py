import pytest
import numpy as np
from ase.atoms import Atoms
from ase.build import bulk as ase_bulk
from ipyatomica.visualise.transforms import add_repeat, apply_transforms, add_resize, add_slice
from jsonextended import plugins, edict
from jsonextended.encoders.ndarray import Encode_NDArray
from ejplugins.utils import load_test_file

from ipyatomica.visualise.repeat_density import ejdata_to_dict, cubesliceplane, atoms_to_rdensity
from ipyatomica.visualise.validation import process_vstruct


@pytest.fixture("function")
def quantum_espresso():
    with plugins.plugins_context([Encode_NDArray]):
        ejdata = load_test_file("scf.qe.charge.json")
        # edict.pprint(data)
        return ejdata


@pytest.fixture("function")
def crystal14():
    with plugins.plugins_context([Encode_NDArray]):
        ejdata = load_test_file("crystal.ech3_dat.prop3d.json")
        # edict.pprint(data)
        return ejdata


# a better way to do this is in the works: https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html
@pytest.fixture(params=['quantum_espresso', 'crystal14'])
def ejdata(request):
    return request.getfuncargvalue(request.param)


def test_ejdata_to_dict(ejdata):
    dct = ejdata_to_dict(ejdata, retrieve_atoms=False)
    assert "elements" in dct
    assert len(dct["elements"]) == 1
    process_vstruct(dct, eltypes=["repeat_density"])


def test_ejdata_to_dict_with_atoms(quantum_espresso):
    dct = ejdata_to_dict(quantum_espresso, retrieve_atoms=True)
    assert "elements" in dct
    assert len(dct["elements"]) == 2
    process_vstruct(dct, eltypes=["repeat_density", "repeat_cell"])


def test_transforms_repeat(quantum_espresso):
    """ see doctests for more specific tests
    """
    dct = ejdata_to_dict(quantum_espresso, retrieve_atoms=False)
    assert dct["elements"][0]["dcube"].shape == (45, 45, 45)
    add_repeat(dct, (2, 1, 1))
    dct = apply_transforms(dct)
    assert dct["elements"][0]["dcube"].shape == (90, 90, 135)


def test_transforms_resize(quantum_espresso):
    """ see doctests for more specific tests
    """
    dct = ejdata_to_dict(quantum_espresso, retrieve_atoms=False)
    assert dct["elements"][0]["dcube"].shape == (45, 45, 45)
    add_resize(dct, .49)
    dct = apply_transforms(dct)
    assert dct["elements"][0]["dcube"].shape == (22, 22, 22)


def test_transforms_slice(quantum_espresso):
    """ see doctests for more specific tests
    """
    dct = ejdata_to_dict(quantum_espresso, retrieve_atoms=False)
    num_nan_init = np.isnan(dct["elements"][0]["dcube"]).sum()
    add_slice(dct, [1, 0, 0], ubound=1)
    dct = apply_transforms(dct)
    num_nan_final = np.isnan(dct["elements"][0]["dcube"]).sum()
    assert num_nan_final > num_nan_init


def test_cubesliceplane_tr_only():
    """ test for a plane which only requires translation
    """
    ccube = np.array([
        [[1., 1., 1.],
         [1., 1., 1.],
         [1., 1., 1.]],
        [[2., 3., 4.],
         [5., 6., 7.],
         [8., 9., 10.]],
        [[20., 20., 20.],
         [20., 20., 20.],
         [20., 20., 20.]]])

    cbounds = (0., 1., 0., 1., 0., 1.)
    corners, corners_xy, gvalues_xy = cubesliceplane(ccube, cbounds, (0.5, 0.5, .5), (0., 0., 1.), cell_size=.25,
                                                     alter_bbox=(.0001, 0., .0001, 0.))

    np.testing.assert_allclose(np.array(corners).round(2),
                               [[-0.0, -0.0, 0.5], [1.0, -0.0, 0.5], [-0.0, 1.0, 0.5], [1.0, 1.0, 0.5]])

    np.testing.assert_allclose(np.array(corners_xy).round(2),
                               [[-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]])

    nan = np.nan
    # print(gvalues_xy.round(2).tolist())
    np.testing.assert_allclose(gvalues_xy.round(2), np.array(
        [[-0.5, -0.5, 2.0], [-0.5, -0.25, 3.5], [-0.5, 0.0, 5.0], [-0.5, 0.25, 6.5],
         [-0.25, -0.5, 2.5], [-0.25, -0.25, 4.0], [-0.25, 0.0, 5.5], [-0.25, 0.25, 7.0],
         [0.0, -0.5, 3.0], [0.0, -0.25, 4.5], [0.0, 0.0, 6.0], [0.0, 0.25, 7.5],
         [0.25, -0.5, 3.5], [0.25, -0.25, 5.0], [0.25, 0.0, 6.5], [0.25, 0.25, 8.0]]
    ))


def test_cubesliceplane_rot_only():
    """ test for a plane which only requires rotation
    """
    ccube = np.array([
        [[4., 4., 4.],
         [1., 1., 1.],
         [1., 1., 1.]],
        [[2., 2., 2.],
         [2., 2., 2.],
         [2., 2., 2.]],
        [[3., 3., 3.],
         [3., 3., 3.],
         [3., 3., 3.]]])

    cbounds = (-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)
    corners, corners_xy, gvalues_xy = cubesliceplane(ccube, cbounds, (0., 0., 0.), (1., 1., 0.), cell_size=.25,
                                                     alter_bbox=(.001, 0., .001, 0.))

    np.testing.assert_allclose(np.array(corners).round(2),
                               [[0.5, -0.5, -0.5], [-0.5, 0.5, -0.5], [0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]])

    np.testing.assert_allclose(np.array(corners_xy).round(2),
                               [[-0.71, -0.5], [0.71, -0.5], [-0.71, 0.5], [0.71, 0.5]])

    nan = np.nan
    # print(gvalues_xy.round(2).tolist())
    np.testing.assert_allclose(gvalues_xy.round(2), np.array(
        [[-0.71, -0.5, 3.99], [-0.71, -0.25, 2.99], [-0.71, 0.0, 2.0], [-0.71, 0.25, 2.5],
         [-0.46, -0.5, 2.93], [-0.46, -0.25, 2.47], [-0.46, 0.0, 2.0], [-0.46, 0.25, 2.5],
         [-0.21, -0.5, 1.87], [-0.21, -0.25, 1.94], [-0.21, 0.0, 2.0], [-0.21, 0.25, 2.5],
         [0.04, -0.5, 1.0], [0.04, -0.25, 1.5], [0.04, 0.0, 2.0], [0.04, 0.25, 2.5],
         [0.29, -0.5, 1.0], [0.29, -0.25, 1.5], [0.29, 0.0, 2.0], [0.29, 0.25, 2.5],
         [0.54, -0.5, 1.0], [0.54, -0.25, 1.5], [0.54, 0.0, 2.0], [0.54, 0.25, 2.5]]
    ))


def test_cubesliceplane_tr_and_rot():
    """ test for a plane which requires both a translation and rotation
    """
    ccube = np.array([
        [[4., 4., 4.],
         [1., 1., 1.],
         [1., 1., 1.]],
        [[2., 2., 2.],
         [2., 2., 2.],
         [2., 2., 2.]],
        [[3., 3., 3.],
         [3., 3., 3.],
         [3., 3., 3.]]])

    cbounds = (0., 1., 0., 1., 0., 1.)
    corners, corners_xy, gvalues_xy = cubesliceplane(ccube, cbounds, (0.5, 0.5, .5), (1., 1., 0.), cell_size=.25,
                                                     alter_bbox=(.001, 0., .001, 0.))

    np.testing.assert_allclose(np.array(corners).round(2),
                               [[1., 0., 0.], [-0., 1., 0.], [1., 0., 1.], [-0., 1., 1.]])

    np.testing.assert_allclose(np.array(corners_xy).round(2),
                               [[-0.71, -0.5], [0.71, -0.5], [-0.71, 0.5], [0.71, 0.5]])

    nan = np.nan
    # print(gvalues_xy.round(2).tolist())
    np.testing.assert_allclose(gvalues_xy.round(2), np.array(
        [[-0.71, -0.5, 3.99], [-0.71, -0.25, 2.99], [-0.71, 0.0, 2.0], [-0.71, 0.25, 2.5],
         [-0.46, -0.5, 2.93], [-0.46, -0.25, 2.47], [-0.46, 0.0, 2.0], [-0.46, 0.25, 2.5],
         [-0.21, -0.5, 1.87], [-0.21, -0.25, 1.94], [-0.21, 0.0, 2.0], [-0.21, 0.25, 2.5],
         [0.04, -0.5, 1.0], [0.04, -0.25, 1.5], [0.04, 0.0, 2.0], [0.04, 0.25, 2.5],
         [0.29, -0.5, 1.0], [0.29, -0.25, 1.5], [0.29, 0.0, 2.0], [0.29, 0.25, 2.5],
         [0.54, -0.5, 1.0], [0.54, -0.25, 1.5], [0.54, 0.0, 2.0], [0.54, 0.25, 2.5]]
    ))


def test_cubesliceplane_tr_and_rot_offset_scentre():
    """ test for a plane which requires both a translation and rotation with an scentre which is not in centre of carray
    """
    ccube = np.array([
        [[4., 4., 4.],
         [1., 1., 1.],
         [1., 1., 1.]],
        [[2., 2., 2.],
         [2., 2., 2.],
         [2., 2., 2.]],
        [[3., 3., 3.],
         [3., 3., 3.],
         [3., 3., 3.]]])

    cbounds = (0., 1., 0., 1., 0., 1.)
    corners, corners_xy, gvalues_xy = cubesliceplane(ccube, cbounds, (0.5, 0.5, 0.3), (1., 1., 0.), cell_size=.25,
                                                     alter_bbox=(.001, 0., .001, 0.))

    np.testing.assert_allclose(np.array(corners_xy).round(2),
                               [[-0.71, -0.5], [0.71, -0.5], [-0.71, 0.5], [0.71, 0.5]])

    np.testing.assert_allclose(np.array(corners).round(2),
                               [[1., 0., 0.], [-0., 1., 0.], [1., 0., 1.], [-0., 1., 1.]])

    nan = np.nan
    # print(gvalues_xy.round(2).tolist())
    np.testing.assert_allclose(gvalues_xy.round(2), np.array(
        [[-0.71, -0.5, 3.99], [-0.71, -0.25, 2.99], [-0.71, 0.0, 2.0], [-0.71, 0.25, 2.5],
         [-0.46, -0.5, 2.93], [-0.46, -0.25, 2.47], [-0.46, 0.0, 2.0], [-0.46, 0.25, 2.5],
         [-0.21, -0.5, 1.87], [-0.21, -0.25, 1.94], [-0.21, 0.0, 2.0], [-0.21, 0.25, 2.5],
         [0.04, -0.5, 1.0], [0.04, -0.25, 1.5], [0.04, 0.0, 2.0], [0.04, 0.25, 2.5],
         [0.29, -0.5, 1.0], [0.29, -0.25, 1.5], [0.29, 0.0, 2.0], [0.29, 0.25, 2.5],
         [0.54, -0.5, 1.0], [0.54, -0.25, 1.5], [0.54, 0.0, 2.0], [0.54, 0.25, 2.5]]
    ))


def test_atoms_to_rdensity_central():
    atoms = Atoms(symbols=["Fe"], scaled_positions=[[0.5, 0.5, 0.5]],
                  cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    atom_map = {"Fe": {"radius": .5, "color_fill": "red"}}
    dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)

    assert c_map == {('Fe', 'red'): 1}
    assert dstruct["elements"][0]["cell_vectors"] == {'a': [1.0, 0.0, 0.0], 'b': [0.0, 1.0, 0.0], 'c': [0.0, 0.0, 1.0]}
    assert dstruct["elements"][0]["centre"] == [0.5, 0.5, 0.5]
    nan = np.nan
    np.testing.assert_allclose(dstruct["elements"][0]["dcube"], np.array(
        [[[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]]]
    ))


def test_atoms_to_rdensity_xoffset():
    atoms = Atoms(symbols=["Fe"], scaled_positions=[[0.75, 0.5, 0.5]],
                  cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    atom_map = {"Fe": {"radius": .5, "color_fill": "red"}}
    dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)

    assert c_map == {('Fe', 'red'): 1}
    assert dstruct["elements"][0]["cell_vectors"] == {'a': [1.0, 0.0, 0.0], 'b': [0.0, 1.0, 0.0], 'c': [0.0, 0.0, 1.0]}
    assert dstruct["elements"][0]["centre"] == [0.5, 0.5, 0.5]
    nan = np.nan
    np.testing.assert_allclose(dstruct["elements"][0]["dcube"], np.array(
        [[[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, 1.0, 1.0, 1.0],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]]]
    ))


def test_atoms_to_rdensity_yoffset():
    atoms = Atoms(symbols=["Fe"], scaled_positions=[[0.5, 0.75, 0.5]],
                  cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    atom_map = {"Fe": {"radius": .5, "color_fill": "red"}}
    dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)

    assert c_map == {('Fe', 'red'): 1}
    assert dstruct["elements"][0]["cell_vectors"] == {'a': [1.0, 0.0, 0.0], 'b': [0.0, 1.0, 0.0], 'c': [0.0, 0.0, 1.0]}
    assert dstruct["elements"][0]["centre"] == [0.5, 0.5, 0.5]
    nan = np.nan
    np.testing.assert_allclose(dstruct["elements"][0]["dcube"], np.array(
        [[[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]]]
    ))


def test_atoms_to_rdensity_zoffset():
    atoms = Atoms(symbols=["Fe"], scaled_positions=[[0.5, 0.5, 0.75]],
                  cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    atom_map = {"Fe": {"radius": .5, "color_fill": "red"}}
    dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)

    assert c_map == {('Fe', 'red'): 1}
    assert dstruct["elements"][0]["cell_vectors"] == {'a': [1.0, 0.0, 0.0], 'b': [0.0, 1.0, 0.0], 'c': [0.0, 0.0, 1.0]}
    assert dstruct["elements"][0]["centre"] == [0.5, 0.5, 0.5]
    nan = np.nan
    np.testing.assert_allclose(dstruct["elements"][0]["dcube"], np.array(
        [[[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, 1.0, 1.0, 1.0, nan],
          [nan, nan, nan, nan, nan]]]
    ))


def test_atoms_to_rdensity_2atoms():
    atoms = Atoms(symbols=["Fe", "S"], scaled_positions=[[0.25, 0.25, 0.25], [0.75, 0.75, 0.75]],
                  cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    atom_map = {"Fe": {"radius": .5, "color_fill": "red"}, "S": {"radius": .5, "color_fill": "blue"}}
    dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)

    assert c_map == {('Fe', 'red'): 1, ('S', 'blue'): 2}
    assert dstruct["elements"][0]["cell_vectors"] == {'a': [1.0, 0.0, 0.0], 'b': [0.0, 1.0, 0.0], 'c': [0.0, 0.0, 1.0]}
    assert dstruct["elements"][0]["centre"] == [0.5, 0.5, 0.5]
    nan = np.nan
    np.testing.assert_allclose(dstruct["elements"][0]["dcube"], np.array(
        [[[1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 2.0, 2.0, 2.0],
          [nan, nan, 2.0, 2.0, 2.0],
          [nan, nan, 2.0, 2.0, 2.0]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, 2.0, 2.0, 2.0],
          [nan, nan, 2.0, 2.0, 2.0],
          [nan, nan, 2.0, 2.0, 2.0]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, 2.0, 2.0, 2.0],
          [nan, nan, 2.0, 2.0, 2.0],
          [nan, nan, 2.0, 2.0, 2.0]]]
    ))


def test_atoms_to_rdensity_non_orthogonal():
    atoms = ase_bulk("Fe")
    atom_map = {"Fe": {"radius": 1.3, "color_fill": "red"}}
    dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)

    assert c_map == {('Fe', 'red'): 1}
    assert dstruct["elements"][0]["cell_vectors"] == {'a': [-1.435, 1.435, 1.435],
                                                      'b': [1.435, -1.435, 1.435],
                                                      'c': [1.435, 1.435, -1.435]}
    assert dstruct["elements"][0]["centre"] == [0.7175, 0.7175, 0.7175]
    nan = np.nan
    np.testing.assert_allclose(dstruct["elements"][0]["dcube"], np.array(
        [[[1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[1.0, 1.0, nan, nan, nan],
          [1.0, 1.0, 1.0, nan, nan],
          [nan, 1.0, 1.0, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]],
         [[nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan],
          [nan, nan, nan, nan, nan]]]
    ))
