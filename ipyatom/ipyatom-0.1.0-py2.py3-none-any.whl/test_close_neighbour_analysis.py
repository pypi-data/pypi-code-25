from ase.build import bulk
from jsonextended import edict

from ipyatom.close_neighbour_analysis import color_by_cna
from ipyatom.repeat_cell import atoms_to_dict


def test_color_by_cna():
    atoms = bulk("Fe")

    dct = atoms_to_dict(atoms, "Iron")
    new_dct = color_by_cna(dct, color_outline=True)

    expected = {'elements': [
        {'type': 'repeat_cell', 'name': 'Iron', 'centre': [0.7175, 0.7175, 0.7175],
         'cell_vectors': {'a': [-1.435, 1.435, 1.435], 'b': [1.435, -1.435, 1.435], 'c': [1.435, 1.435, -1.435]},
         "color_bbox": "black",
         'sites': [
             {'ccoord': [0.0, 0.0, 0.0],
              'label': 'Fe, BCC',
              'anum': 26,
              'color_fill': 'green',
              'color_outline': 'green',
              'radius': 1.32, 'transparency': 1,
              'cell': [0, 0, 0]}],
         'transforms': []}],
        'transforms': []}

    assert edict.diff(new_dct, expected, np_allclose=True) == {}
