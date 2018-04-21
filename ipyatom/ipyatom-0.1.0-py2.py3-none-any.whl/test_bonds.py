from ase.build import bulk
from ipyatom.bonds import compute_bonds, add_bonds
from ipyatom.repeat_cell import atoms_to_dict
from jsonextended import edict


def test_add_bonds():

    atoms = bulk("NaCl", "rocksalt", 5.64)
    dct = atoms_to_dict(atoms, "NaCl")
    print()
    # print(dct)

    dct = add_bonds(dct, "Na", "Cl", 4, 0.5)

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
             {'label': 'Cl',
              'ccoord': [2.82, 0.0, 0.0],
              'cell': [0, 0, 0], 'radius': 1.02, 'color_fill': '#1ff01f',
              'color_outline': None, 'transparency': 1, 'anum': 17}],
         'bonds': [{
            "label": "Na",
            "coord_label": "Cl",
            "radius": 0.5,
            "max_dist": 4,
            "include_periodic": True,
            "color_by_dist": False,
            "cmap_name": "jet",
            "drange": (0, 10)
            }],
         'transforms': []}],
        'transforms': []}

    assert edict.diff(dct, expected_dct, np_allclose=True) == {}


def test_bonds():
    atoms = bulk("NaCl", "rocksalt", 5.64)
    dct = atoms_to_dict(atoms, "NaCl")
    print()
    # print(dct)

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
             {'label': 'Cl',
              'ccoord': [2.82, 0.0, 0.0],
              'cell': [0, 0, 0], 'radius': 1.02, 'color_fill': '#1ff01f',
              'color_outline': None, 'transparency': 1, 'anum': 17}],
         'bonds': [], 'transforms': []}],
        'transforms': []}

    dct['elements'][0]['bonds'] = [
        {
            "label": "Na",
            "coord_label": "Cl",
            "radius": 1,
            "max_dist": 4,
            "include_periodic": False,
            "color_by_dist": False,
            "cmap_name": "jet",
            "drange": (0, 10)
        },
        {
            "label": "Na",
            "coord_label": "Cl",
            "radius": 2,
            "max_dist": 4,
            "include_periodic": True,
            "color_by_dist": False,
            "cmap_name": "jet",
            "drange": (0, 10)
        },
        {
            "label": "Na",
            "coord_label": "Na",
            "radius": 3,
            "max_dist": 4,
            "include_periodic": False,
            "color_by_dist": False,
            "cmap_name": "jet",
            "drange": (0, 10)
        },
        {
            "label": "Na",
            "coord_label": "Na",
            "radius": 4,
            "max_dist": 4,
            "include_periodic": True,
            "color_by_dist": False,
            "cmap_name": "jet",
            "drange": (0, 10)
        },
    ]

    bonds = compute_bonds(dct)

    # edict.pprint(dict(enumerate(bonds)))
    #print(bonds)
    expected_bonds = [[[0.0, 0.0, 0.0], [2.82, 0.0, 0.0], '#ab5cf2', '#1ff01f', 1],
                      [[0.0, 0.0, 0.0], [0.0, 2.82, 0.0], '#ab5cf2', '#1ff01f', 2],
                      [[0.0, 0.0, 0.0], [0.0, -2.82, 0.0], '#ab5cf2', '#1ff01f', 2],
                      [[0.0, 0.0, 0.0], [0.0, 0.0, 2.82], '#ab5cf2', '#1ff01f', 2],
                      [[0.0, 0.0, 0.0], [-2.82, 0.0, 0.0], '#ab5cf2', '#1ff01f', 2],
                      [[0.0, 0.0, 0.0], [2.82, 0.0, 0.0], '#ab5cf2', '#1ff01f', 2],
                      [[0.0, 0.0, 0.0], [0.0, 0.0, -2.82], '#ab5cf2', '#1ff01f', 2],
                      [[0.0, 0.0, 0.0], [0.0, 2.82, -2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [-2.82, 2.82, 0.0], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [2.82, 2.82, 0.0], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [0.0, -2.82, 2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [-2.82, 0.0, -2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [0.0, 2.82, 2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [-2.82, -2.82, 0.0], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [-2.82, 0.0, 2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [0.0, -2.82, -2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [2.82, 0.0, -2.82], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [2.82, -2.82, 0.0], '#ab5cf2', '#ab5cf2', 4],
                      [[0.0, 0.0, 0.0], [2.82, 0.0, 2.82], '#ab5cf2', '#ab5cf2', 4]]

    assert edict.diff(bonds, expected_bonds, np_allclose=True) == {}
