# !/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

import numpy as np
from ipyatomica.visualise import process_vstruct
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from scipy.spatial.ckdtree import cKDTree


# TODO prune identical bonds
def compute_bonds(vstruct, max_neighbours=16, min_dist=0.1):
    """

    Parameters
    ----------
    vstruct: dict
    max_neighbours: int
        maximum number of neighbours to consider
    min_dist: float
        minimum distance to be considered
    """
    vstruct = copy.deepcopy(vstruct)
    vstruct = process_vstruct(vstruct)  # , ["repeat_cell"])
    bonds = []

    for element in vstruct["elements"]:
        if element["type"] != "repeat_cell":
            continue

        lattice = [element["cell_vectors"]["a"], element["cell_vectors"]["b"], element["cell_vectors"]["c"]]
        a, b, c = np.asarray(lattice)
        ccoords = np.array([s["ccoord"] for s in element["sites"]])
        labels = np.array([s["label"] for s in element["sites"]])
        color_fills = np.array([s["color_fill"] for s in element["sites"]])
        # transparency = np.array([s["transparency"] for s in element["sites"]])

        for bond in element["bonds"]:

            coords = ccoords.copy()[labels == bond["label"]]
            ccolor_fill = color_fills.copy()[labels == bond["label"]]

            lcoords = ccoords.copy()[labels == bond["coord_label"]]
            lcolor_fill = color_fills.copy()[labels == bond["coord_label"]]

            if len(coords) == 0 or len(lcoords) == 0:
                continue

            if bond["color_by_dist"]:
                norm = Normalize(vmin=bond["drange"][0], vmax=bond["drange"][1])
                cmap = get_cmap(bond["cmap_name"])

                def cmap_func(x):
                    r, g, b, a = cmap(norm(x))
                    return r, g, b

            # repeat coordinates in all direction, where original coordinates are first
            if bond["include_periodic"]:
                lcoords = np.concatenate((
                    lcoords, lcoords - a, lcoords + a))
                lcolor_fill = np.concatenate((
                    lcolor_fill, lcolor_fill, lcolor_fill))
                lcoords = np.concatenate((
                    lcoords, lcoords - b, lcoords + b))
                lcolor_fill = np.concatenate((
                    lcolor_fill, lcolor_fill, lcolor_fill))
                lcoords = np.concatenate((
                    lcoords, lcoords - c, lcoords + c))
                lcolor_fill = np.concatenate((
                    lcolor_fill, lcolor_fill, lcolor_fill))

            # compute nearest neighbours
            ltree = cKDTree(lcoords)
            all_dists, all_ids = ltree.query(coords, k=max_neighbours + 1, distance_upper_bound=bond["max_dist"])

            # construct a mapping of atom ids to nearest neighbour ids
            for i, (dists, ids) in enumerate(zip(all_dists, all_ids)):
                mask = np.logical_and(dists > min_dist, dists < np.inf)
                for cid, dist in zip(ids[mask], dists[mask]):
                    if bond["color_by_dist"]:
                        cfill = lfill = cmap_func(dist)
                    else:
                        cfill, lfill = ccolor_fill[i], lcolor_fill[cid]
                    bonds.append([coords[i].tolist(), lcoords[cid].tolist(),
                                  cfill, lfill, bond["radius"]])

    return bonds


def add_bonds(vstruct, label, coord_label, max_dist=3.5, bradius=0.1, include_periodic=True, elements=None,
              color_by_dist=False, cmap_name="jet", drange=(0, 10)):
    """ add bonds to a vstruct

    Parameters
    ----------
    vstruct: dict
    label: str
        the atom type to compute bonds from
    coord_label: str
        the coordinating atom type
    max_dist: float
        maximum distance of coordinating atom
    bradius: float
        radius of bond cylinder
    include_periodic: boolean
        include bonds to atoms in neighbouring periodic cells
    elements: None or list of ints
        if None add to all "repeat_cell" elements
    color_by_dist: bool
        if True, color bonds by their length
    cmap_name: str
        the matplotlib colormap to use if color_by_dist is True
    drange: tuple of float
        the distance range (min, max) to use if color_by_dist is True
    """
    new_vstuct = process_vstruct(vstruct, deepcopy=True)
    for i, element in enumerate(new_vstuct["elements"]):
        if element["type"] != "repeat_cell":
            continue
        if elements is None or i in elements:
            element["bonds"].append({
                "label": label,
                "coord_label": coord_label,
                "radius": bradius,
                "max_dist": max_dist,
                "include_periodic": include_periodic,
                "color_by_dist": color_by_dist,
                "cmap_name": cmap_name,
                "drange": drange
            })
    return new_vstuct


if __name__ == "__main__":
    test_vstruct = {'elements': [{'bonds': [{'coord_label': 'S',
                                             'include_periodic': True,
                                             'label': 'Fe',
                                             'max_dist': 3,
                                             'radius': 0.1,
                                             "color_by_dist": False,
                                             "cmap_name": "jet",
                                             "drange": (0, 10),
                                             },
                                            {'coord_label': 'Fe',
                                             'include_periodic': True,
                                             'label': 'S',
                                             'max_dist': 3,
                                             'radius': 0.1,
                                             "color_by_dist": False,
                                             "cmap_name": "jet",
                                             "drange": (0, 10),
                                             },
                                            {'coord_label': 'S',
                                             'include_periodic': True,
                                             'label': 'S',
                                             'max_dist': 3,
                                             'radius': 0.1,
                                             "color_by_dist": False,
                                             "cmap_name": "jet",
                                             "drange": (0, 10),
                                             }],
                                  'cell_vectors': {'a': [-1.6593964128446632e-16,
                                                         2.7099999999999995,
                                                         2.7099999999999995],
                                                   'b': [2.7099999999999995, 0.0, 2.7099999999999995],
                                                   'c': [2.7099999999999995, 2.7099999999999995,
                                                         3.3187928256893265e-16]},
                                  'centre': [0.0, 0.0, 0.0],
                                  'color_bbox': 'black',
                                  'name': '',
                                  'sites': [{'anum': 26,
                                             'ccoord': [-1.3549999999999998, -1.3549999999999998, -1.3549999999999993],
                                             'cell': [0, 0, 0],
                                             'color_fill': '#e06633',
                                             'color_outline': None,
                                             'label': 'Fe',
                                             'radius': 1.32,
                                             'transparency': 1},
                                            {'anum': 16,
                                             'ccoord': [1.355, 1.355, 1.355],
                                             'cell': [0, 0, 0],
                                             'color_fill': '#b2b200',
                                             'color_outline': None,
                                             'label': 'S',
                                             'radius': 1.05,
                                             'transparency': 1}],
                                  'transforms': [],
                                  'type': 'repeat_cell'}],
                    'transforms': []}

    print(compute_bonds(test_vstruct))
