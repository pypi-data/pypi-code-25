import numpy as np
from ipyatomica.visualise.render_ivol import _get_cylinder_mesh, create_ivol
from jsonextended import edict


def test_get_cylinder_mesh():
    p1 = [0.8452500000000001, -0.45025399999999993, 2.3686249999999993]
    p2 = [-2.5357499999999997, -0.45025399999999993, 2.3686249999999993]
    radius = 0.1
    segments = 50
    mesh_pts = _get_cylinder_mesh(p1, p2, radius, segments)
    assert np.count_nonzero(~np.isnan(mesh_pts))


def test_render_atoms_simple():
    dstruct = {
        'type': 'repeat_density',
        'dtype': 'charge',
        'name': '',
        'dcube': np.ones((3, 3, 3)),
        'centre': [0, 0, 0],
        'cell_vectors': {
            'a': [2., 0, 0],
            'b': [0, 2., 0],
            'c': [0, 0, 2.]},
        'color_bbox': 'black',
        'transforms': []
    }
    cstruct = {
        'type': 'repeat_cell',
        'name': '',
        'centre': [0, 0, 0],
        'cell_vectors': {
            'a': [2., 0, 0],
            'b': [0, 2., 0],
            'c': [0, 0, 2.]},
        'color_bbox': 'black',
        'sites': [{
            'label': "Fe",
            'ccoord': [1, 1, 1],
            'color_fill': "red",
            'color_outline': None,
            'transparency': 1,
            'radius': 1,
        }],
        'bonds': [],
        'transforms': []
    }
    vstruct = {"elements": [dstruct, cstruct], "transforms": []}
    new_struct, fig, controls = create_ivol(vstruct)

    output = edict.apply(edict.filter_keys(new_struct, ["ivol"], list_of_dicts=True),
                         "ivol", lambda x: [v.__class__.__name__ for v in x], list_of_dicts=True)
    expected = {'elements': [{'ivol': ['Figure', 'Mesh']}, {'ivol': ['Mesh', 'Scatter']}]}

    assert output == expected
