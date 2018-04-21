import numpy as np
from ase.build import bulk
from ipyatomica.visualise.repeat_cell import atoms_to_dict
from ipyatomica.visualise.plot_mpl import plot_atoms_top, plot_slice


def test_plot_atoms_top():
    fe = bulk("Fe").repeat((5, 5, 5))

    dct = atoms_to_dict(fe)
    plot_atoms_top(dct, linewidth=5)


def test_plot_slice():
    instruct = {
        "transforms": [],
        "elements": [
            {"type": "repeat_density",
             "name": "Test",
             "dtype": "other",
             "transforms": [],
             "color_bbox": None,
             "centre": [.5, 1, .5],
             "cell_vectors": {
                 "a": [1, 1, 0],
                 "b": [0, 1, 0],
                 "c": [0, 0, 1]},
             "dcube": np.array([
                 [[1., 1., 1.],
                  [1., 1., 1.],
                  [1., 1., 1.]],
                 [[2., 3., 4.],
                  [5., 6., 7.],
                  [8., 9., 11.]],
                 [[20., 20., 20.],
                  [20., 20., 20.],
                  [20., 20., 20.]]])
             },
            {"type": "repeat_density",
             "name": "Test",
             "dtype": "other2",
             "transforms": [],
             "color_bbox": None,
             "centre": [.5, 1, .5],
             "cell_vectors": {
                 "a": [1, 1, 0],
                 "b": [0, 1, 0],
                 "c": [0, 0, 1]},
             "dcube": np.array([
                 [[1., 1., 1.],
                  [1., 1., 1.],
                  [1., 1., 1.]],
                 [[2., 3., 4.],
                  [5., 6., 7.],
                  [8., 9., 10.]],
                 [[20., 20., 20.],
                  [20., 20., 20.],
                  [20., 20., 20.]]]) * 0.00001
             },
            {"type": "repeat_cell",
             "name": "Test",
             "transforms": [],
             "bonds": [],
             "color_bbox": None,
             "centre": [.5, 1, .5],
             "cell_vectors": {
                 "a": [1, 1, 0],
                 "b": [0, 1, 0],
                 "c": [0, 0, 1]},
             "sites": [
                 {
                     "radius": .5,
                     "transparency": 1,
                     "label": "Fe",
                     "ccoord": [.5, 1, .5],
                     "color_fill": "red",
                     "color_outline": None
                 },
                 {
                     "radius": .5,
                     "transparency": 1,
                     "label": "S",
                     "ccoord": [.5, 0, .5],
                     "color_fill": "blue",
                     "color_outline": None
                 }

             ]

             }

        ]
    }

    fig1, axes1 = plot_slice(instruct, (0.5, 0.5, 0.5), (0., 0., 1.),
                             cell_size=.001, min_voxels=10000, cmap_range=(None, None),
                             contourf=[True, True, False], bval=[np.nan, np.nan, 0],
                             show_corners=[False, True, False], cbar_tick_rot=45)
