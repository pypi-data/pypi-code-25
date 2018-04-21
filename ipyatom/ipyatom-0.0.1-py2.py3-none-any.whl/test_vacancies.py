import numpy as np

from ase.build import bulk
from ipyatomica.visualise.repeat_cell import atoms_to_dict
from jsonextended import edict

from ipyatomica.visualise.vacancies import compute_vacancies, add_vacancies


def test_compute_vacancies():
    print()
    vac_list = compute_vacancies([[0, 0, 0], [2, 0, 0]],
                                 [[4, 0, 0], [0, 2, 0], [0, 0, 2]], [2, 1, 1],
                                 grid_spacing=0.1, min_dist=1.5, remove_dups=True)
    assert np.allclose(vac_list, [[1, 1, 1], [3, 1, 1]], atol=0.1)


def test_compute_vacancies_vacuum():

    vac_list = compute_vacancies([[0, 0, 0], [0, 0, 2]],
                                 [[4, 0, 0], [0, 2, 0], [0, 0, 20]], [2, 1, 10],
                                 grid_spacing=0.1, min_dist=1.5, remove_dups=True, ignore_vacuum=0)
    assert np.allclose(vac_list, [[2, 1, 1]], atol=0.1)


def test_add_vacancies():
    atoms = bulk("NaCl", "rocksalt", 5.64)
    atoms.pop(1)
    dct = atoms_to_dict(atoms, "NaCl")
    print()
    #edict.pprint(dct)

    dct = add_vacancies(dct, min_dist=2, radius=1)
    edict.pprint(dct)

    expected_dct = {'elements': [
        {'type': 'repeat_cell', 'name': 'NaCl',
         'centre': [2.82, 2.82, 2.82], 'color_bbox': 'black',
         'cell_vectors': {'a': [0.0, 2.82, 2.82],
                          'b': [2.82, 0.0, 2.82],
                          'c': [2.82, 2.82, 0.0]},
         'sites': [
             {'label': 'Na',
              'ccoord': [0.0, 0.0, 0.0],
              'cell': [0, 0, 0], 'radius': 1.66, 'color_fill': '#ab5cf2',
              'color_outline': None, 'transparency': 1, 'anum': 11},
             {'label': 'Vac',
              'ccoord': [2.82, 2.82, 2.82],
              'cell': [0, 0, 0], 'radius': 1, 'color_fill': 'grey',
              'color_outline': None, 'transparency': 1}],
         'bonds': [],
         'transforms': []}],
        'transforms': []}

    assert edict.diff(dct, expected_dct, np_allclose=True) == {}
