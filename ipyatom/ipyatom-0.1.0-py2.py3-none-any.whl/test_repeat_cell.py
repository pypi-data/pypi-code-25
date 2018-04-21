from ase.build import bulk
from jsonextended import edict
from jsonschema import validate

from ipyatom.repeat_cell import (_atom_map_schema, atoms_to_dict, ejdata_to_dict,
                                              get_default_atom_map, color_by_mpl)
from ipyatom.transforms import apply_transforms, add_repeat, add_translate_to, add_slice


def test_get_default_atom_map():
    adict = get_default_atom_map()
    validate(adict, _atom_map_schema)


def test_atoms_to_dict():
    atoms = bulk("Fe")
    dct = atoms_to_dict(atoms, "Iron", charge=[.5])
    expected = {'elements':
                    [{'type': 'repeat_cell',
                      'name': 'Iron',
                      'centre': [0.7175, 0.7175, 0.7175],
                      'cell_vectors': {'a': [-1.435, 1.435, 1.435],
                                       'b': [1.435, -1.435, 1.435],
                                       'c': [1.435, 1.435, -1.435]},
                      'color_bbox': "black",
                      'sites': [
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [0.0, 0.0, 0.0],
                           # 'fcoord': [0.0, 0.0, 0.0],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (0, 0, 0),
                           'charge': 0.5
                           }
                      ],
                      'bonds': [],
                      'transforms': []}],
                "transforms": []}
    assert edict.diff(dct, expected, np_allclose=True) == {}


def test_ejdict_to_dict():
    atoms = bulk("Fe")
    ejdata = {"fcoords": atoms.get_scaled_positions(),
              "cell_vectors": {k: v for k,v in zip(["a", "b", "c"],
                                                    atoms.get_cell())},
              "symbols": atoms.get_chemical_symbols()}

    dct = ejdata_to_dict(ejdata, "Iron", charge=[.5])
    expected = {'elements':
                    [{'type': 'repeat_cell',
                      'name': 'Iron',
                      'centre': [0.7175, 0.7175, 0.7175],
                      'cell_vectors': {'a': [-1.435, 1.435, 1.435],
                                       'b': [1.435, -1.435, 1.435],
                                       'c': [1.435, 1.435, -1.435]},
                      'color_bbox': "black",
                      'sites': [
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [0.0, 0.0, 0.0],
                           # 'fcoord': [0.0, 0.0, 0.0],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (0, 0, 0),
                           'charge': 0.5
                           }
                      ],
                      'bonds': [],
                      'transforms': []}],
                "transforms": []}
    assert edict.diff(dct, expected, np_allclose=True) == {}


def test_transforms_repeat():
    atoms = bulk("Fe")
    dct = atoms_to_dict(atoms, "Iron")
    add_repeat(dct, (2, 0, 0))
    expected = {'elements':
                    [{'type': 'repeat_cell',
                      'name': 'Iron',
                      'centre': [-0.7175, 2.1525, 2.1525],
                      'cell_vectors': {'a': [-4.305, 4.305, 4.305],
                                       'b': [1.435, -1.435, 1.435],
                                       'c': [1.435, 1.435, -1.435]},
                      'color_bbox': "black",
                      'sites': [
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [0.0, 0.0, 0.0],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (0, 0, 0)},
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [-1.435, 1.435, 1.435],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (1, 0, 0)},
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [-2.87, 2.87, 2.87],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (2, 0, 0)}
                      ],
                      'bonds': [],
                      'transforms': []}],
                "transforms": []}
    assert edict.diff(apply_transforms(dct), expected, np_allclose=True) == {}


def test_transforms_translate_to():
    atoms = bulk("Fe")
    dct = atoms_to_dict(atoms, "Iron")
    add_translate_to(dct, (1., 1., 1.))
    expected = {'elements':
                    [{'type': 'repeat_cell',
                      'name': 'Iron',
                      'centre': [1., 1., 1.],
                      'cell_vectors': {'a': [-1.435, 1.435, 1.435],
                                       'b': [1.435, -1.435, 1.435],
                                       'c': [1.435, 1.435, -1.435]},
                      'color_bbox': "black",
                      'sites': [
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [0.2825, 0.2825, 0.2825],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (0, 0, 0)},
                      ],
                      'bonds': [],
                      'transforms': []}],
                "transforms": []}
    assert edict.diff(apply_transforms(dct), expected, np_allclose=True) == {}


def test_transforms_slice():
    atoms = bulk("Fe").repeat((5, 5, 5))
    dct = atoms_to_dict(atoms, "Iron")
    add_translate_to(dct, (0, 0, 0))
    add_slice(dct, (1, 0, 0), lbound=0, ubound=3)
    add_slice(dct, (0, 1, 0), lbound=0, ubound=3)
    add_slice(dct, (0, 0, 1), lbound=0, ubound=3)
    expected = {'elements':
                    [{'type': 'repeat_cell',
                      'name': 'Iron',
                      'centre': [0., 0., 0.],
                      'cell_vectors': {'a': [-7.175, 7.175, 7.175],
                                       'b': [7.175, -7.175, 7.175],
                                       'c': [7.175, 7.175, -7.175]},
                      'color_bbox': "black",
                      'sites': [
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [0.7175, 0.7175, 0.7175],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (0, 0, 0)},
                          {'label': 'Fe',
                           'anum': 26,
                           'ccoord': [2.1525, 2.1525, 2.1525],
                           'color_fill': '#e06633',
                           'color_outline': None,
                           'radius': 1.32,
                           'transparency': 1,
                           'cell': (0, 0, 0)},
                      ],
                      'bonds': [],
                      'transforms': []}],
                "transforms": []}
    assert edict.diff(apply_transforms(dct), expected, np_allclose=True) == {}


def test_color_by_mpl():
    atoms = bulk("Fe").repeat((2, 2, 1))
    dct = atoms_to_dict(atoms, "Iron", charge=[.5, -.5, .1, -.1])
    new_dct = color_by_mpl(dct, "charge", vrange=(-1, 1), outline_color=True)

    expected = {'elements': [{'type': 'repeat_cell', 'name': 'Iron', 'centre': [0.7175, 0.7175, 2.1525],
                              'cell_vectors': {'a': [-2.87, 2.87, 2.87], 'b': [2.87, -2.87, 2.87],
                                               'c': [1.435, 1.435, -1.435]},
                              'color_bbox': "black",
                              'sites': [
                                  {'ccoord': [0.0, 0.0, 0.0], 'label': 'Fe', 'anum': 26,
                                   'color_fill': (1.0, 0.58169934640522891, 0.0),
                                   'color_outline': (1.0, 0.58169934640522891, 0.0),
                                   'radius': 1.32, 'transparency': 1, 'cell': [0, 0, 0], 'charge': 0.5},
                                  {'ccoord': [1.435, -1.435, 1.435], 'label': 'Fe', 'anum': 26,
                                   'color_fill': (0.0, 0.50392156862745097, 1.0),
                                   'color_outline': (0.0, 0.50392156862745097, 1.0),
                                   'radius': 1.32, 'transparency': 1, 'cell': [0, 0, 0], 'charge': -0.5},
                                  {'ccoord': [-1.435, 1.435, 1.435], 'label': 'Fe', 'anum': 26,
                                   'color_fill': (0.64199873497786197, 1.0, 0.32574320050600891),
                                   'color_outline': (0.64199873497786197, 1.0, 0.32574320050600891),
                                   'radius': 1.32, 'transparency': 1, 'cell': [0, 0, 0], 'charge': 0.1},
                                  {'ccoord': [0.0, 0.0, 2.87], 'label': 'Fe', 'anum': 26,
                                   'color_fill': (0.3257432005060088, 1.0, 0.6419987349778622),
                                   'color_outline': (0.3257432005060088, 1.0, 0.6419987349778622),
                                   'radius': 1.32, 'transparency': 1, 'cell': [0, 0, 0], 'charge': -0.1}],
                              'bonds': [],
                              'transforms': []}],
                'transforms': []}

    assert edict.diff(new_dct, expected, np_allclose=True) == {}
