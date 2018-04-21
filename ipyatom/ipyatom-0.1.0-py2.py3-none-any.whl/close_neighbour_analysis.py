# !/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import warnings
from collections import Counter

import numpy as np
from scipy.spatial.ckdtree import cKDTree

from ipyatom import process_vstruct

with warnings.catch_warnings(record=True):
    warnings.filterwarnings("ignore", category=ImportWarning)
    import pymatgen as pym


def _create_tree_from_edges(edges):
    """

    Examples
    --------
    >>> from pprint import pprint
    >>> pprint(_create_tree_from_edges([[1,2],[0,1],[2,3],[8,9],[0,3]]))
    {0: [1, 3], 1: [2, 0], 2: [1, 3], 3: [2, 0], 8: [9], 9: [8]}

    Parameters
    ----------
    edges : list of pairs

    """
    tree = {}
    for v1, v2 in edges:
        tree.setdefault(v1, []).append(v2)
        tree.setdefault(v2, []).append(v1)
    return tree


def _longest_path(tree, start, lastnode=None):
    """a recursive function to compute a maximum unbroken chain given a tree

    Parameters
    ----------
    tree : object
    start  : int

    Examples
    --------
    >>> _longest_path({0: [1, 3], 1: [2, 0], 2: [1, 3], 3: [2,0], 8: [9], 9: [8]}, 0)
    [0, 3, 2, 1, 0]

    """
    if start not in tree:
        return []
    new_tree = tree.copy()
    # nodes = new_tree.pop(start) # can use if don't want to complete loops
    nodes = new_tree[start]
    new_tree[start] = []  # don't get stuck in loop

    path = []
    for node in nodes:
        if node == lastnode:
            continue  # can't go back to lastnode, e.g. 1->2->1
        new_path = _longest_path(new_tree, node, start)
        if len(new_path) > len(path):
            path = new_path
    path.append(start)
    return path


def _cna_compute_jkl(coords, lattice, min_dist=0.1, max_dist=3.5, max_neighbours=16, repeat_cell=True):
    """common neighbour analysis to compute local coordination environment of atoms in unit cell

    Parameters
    ----------
    coords: numpy.array((N,3))
        repeat_cell elements
    lattice: numpy.array((3,3))
        lattice vectors
    min_dist: float
        minimum distance to be considered
    max_dist: float
        maximum distance to be considered
    max_neighbours: int
        maximum number of neighbours to consider
    repeat_cell : bool
        whether to repeat cell in all directions before computing nearest neighbours

    Returns
    -------
    jkl_counts: list of collections.Counter

    Notes
    -----
    Based on Faken, Daniel and Jonsson, Hannes,
    'Systematic analysis of local atomic structure combined with 3D computer graphics',
    March 1994, DOI: 10.1016/0927-0256(94)90109-0

    Examples
    --------
    >>> from pprint import pprint

    BCC IRON
    >>> lattice = pym.Lattice.cubic(2.866)
    >>> struct = pym.Structure.from_spacegroup(229, lattice,["Fe"],[[0,0,0]])
    >>> pprint(_cna_compute_jkl(struct.cart_coords,struct.lattice.matrix))
    [Counter({(6, 6, 6): 8, (4, 4, 4): 6}), Counter({(6, 6, 6): 8, (4, 4, 4): 6})]

    FCC Aluminium
    >>> lattice = pym.Lattice.cubic(4.05)
    >>> struct = pym.Structure.from_spacegroup(225, lattice,["Al"],[[0,0,0]])
    >>> pprint(_cna_compute_jkl(struct.cart_coords,struct.lattice.matrix))
    [Counter({(4, 2, 1): 12}),
     Counter({(4, 2, 1): 12}),
     Counter({(4, 2, 1): 12}),
     Counter({(4, 2, 1): 12})]

    HCP Magnesium
    >>> lattice = pym.Lattice.hexagonal(3.21, 5.21)
    >>> struct = pym.Structure.from_spacegroup(194, lattice,["Mg"],[[1/3.,2/3.,0.25]])
    >>> pprint([dict(c) for c in _cna_compute_jkl(struct.cart_coords,struct.lattice.matrix)])
    [{(4, 2, 1): 6, (4, 2, 2): 6}, {(4, 2, 1): 6, (4, 2, 2): 6}]


    Diamond Carbon
    >>> lattice = pym.Lattice.cubic(3.57)
    >>> struct = pym.Structure.from_spacegroup(227, lattice,["C"],[[0,0,0]])
    >>> pprint(_cna_compute_jkl(struct.cart_coords,struct.lattice.matrix))
    [Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4}),
     Counter({(5, 4, 3): 12, (6, 6, 3): 4})]

    Icosohedral a-Boron NOT WORKING
    # >>> lattice = pym.Lattice.hexagonal(4.9179, 12.5805)
    # >>> struct = pym.Structure.from_spacegroup(166, lattice,["B", "B"],
    # ...                                        [[.11886, .88114, .89133], [.19686, .80314, .02432]])
    # >>> struct = struct.get_primitive_structure()
    # >>> pprint(cna_compute_jkl(struct.cart_coords, struct.lattice.matrix))


    """

    # repeat coordinates in all direction, where original coordinates are first
    coords = np.asarray(coords)
    a, b, c = np.asarray(lattice)
    if repeat_cell:
        lcoords = np.concatenate((
            coords, coords - a, coords + a))
        lcoords = np.concatenate((
            lcoords, lcoords - b, lcoords + b))
        lcoords = np.concatenate((
            lcoords, lcoords - c, lcoords + c))
    else:
        lcoords = coords.copy()

    # compute nearest neighbours
    ltree = cKDTree(lcoords)
    all_dists, all_ids = ltree.query(lcoords, k=max_neighbours + 1, distance_upper_bound=max_dist)

    # construct a mapping of atom ids to nearest neighbour ids
    nn_ids = {}
    for dists, ids in zip(all_dists, all_ids):
        mask = np.logical_and(dists > min_dist, dists < np.inf)
        # assume first id is of that atom, i.e. dists[0]==0
        assert dists[0] == 0, "first dist does not have distance 0"
        nn_ids[ids[0]] = ids[mask]

    # compute cna parameters for each atom in original cell
    jkl_counts = []
    for i in range(coords.shape[0]):
        jkls = []
        for neighbour in nn_ids[i]:
            # j is number of shared nearest neighbours
            shared_neighbours = set(nn_ids[neighbour]).intersection(nn_ids[i])
            j = len(shared_neighbours)
            # k is number of bonds between nearest neighbours
            nn_bonds = []
            for shared_neighbour in shared_neighbours:
                for nn_bond in set(nn_ids[shared_neighbour]).intersection(shared_neighbours):
                    if sorted((shared_neighbour, nn_bond)) not in nn_bonds:
                        nn_bonds.append(sorted((shared_neighbour, nn_bond)))
            k = len(nn_bonds)
            # l is longest chain of nearest neighbour bonds
            tree = _create_tree_from_edges(nn_bonds)
            chain_lengths = [0]
            for node in tree.keys():
                chain_lengths.append(len(_longest_path(tree, node)) - 1)
            l = max(chain_lengths)
            jkls.append((j, k, l))

        jkl_counts.append(Counter(jkls))

    return jkl_counts


def _approx_eq(i, j, accuracy):
    """

    Parameters
    ----------
    i: float
    j: float
    accuracy: float

    Returns
    -------

    """
    return j * accuracy <= i <= j + j * (1 - accuracy)


_CNA_COLORMAP = (('BCC', 'green'), ('FCC', 'blue'), ('HCP', 'orange'), ('Diamond', 'red'), ('Icosahedral', 'yellow'),
                 ('Other', 'grey'))


def _cna_jkl_to_categories(jkl_counts, accuracy=1., colors=None):
    """ convert jkl to categories and colors

    Parameters
    ----------
    jkl_counts: list of collections.Counter
    accuracy: float
        +/- error in number of jkl counts
    colors: list or dict
        mapping of cna category names to colors, to override defaults; {defaults}

    Returns
    -------
    categories: list or str
    colors: list of tuples or str
        (r,g,b), hex or html color name
    """
    color_map = dict(_CNA_COLORMAP)
    if colors is not None:
        color_map.update(colors)
    cattypes = []
    colorlst = []
    for counter in jkl_counts:
        if _approx_eq(counter[(4, 2, 1)], 6, accuracy) and _approx_eq(counter[(4, 2, 2)], 6, accuracy):
            cattypes.append('HCP')
            colorlst.append(color_map['HCP'])
        elif _approx_eq(counter[(4, 2, 1)], 12, accuracy):
            cattypes.append('FCC')
            colorlst.append(color_map['FCC'])
        elif _approx_eq(counter[(6, 6, 6)], 8, accuracy) and _approx_eq(counter[(4, 4, 4)], 6, accuracy):
            cattypes.append('BCC')
            colorlst.append(color_map['BCC'])
        elif _approx_eq(counter[(5, 4, 3)], 12, accuracy) and _approx_eq(counter[(6, 6, 3)], 4, accuracy):
            cattypes.append('Diamond')
            colorlst.append(color_map['Diamond'])
        elif _approx_eq(counter[(5, 5, 5)], 12, accuracy):
            cattypes.append('Icosahedral')
            colorlst.append(color_map['Icosahedral'])
        else:
            cattypes.append('Other')
            colorlst.append(color_map['Other'])

    return cattypes, colorlst


_cna_jkl_to_categories.__doc__.format(defaults=dict(_CNA_COLORMAP))


def color_by_cna(vstruct, color_fill=True, color_outline=False, merge_label=True,
                 min_dist=0.1, max_dist=3.5, max_neighbours=16, repeat_cell=True,
                 jkl_accuracy=1, colors=()):
    """

    Parameters
    ----------
    vstruct: dict
    color_fill: bool
        whether to change atom fill color
    color_outline: bool
        whether to change atom outline color
    merge_label: bool
        whether to merge existing label, e.g. "Fe" -> "Fe, BCC"
    min_dist: float
        minimum distance to be considered
    max_dist: float
        maximum distance to be considered
    max_neighbours: int
        maximum number of neighbours to consider
    repeat_cell : bool
        whether to repeat cell in all directions before computing nearest neighbours
    jkl_accuracy: float
        +/- error in number of jkl counts
    colors: list or dict
        mapping of cna category names to colors, to override defaults; {defaults}

    Returns
    -------

    """
    vstruct = copy.deepcopy(vstruct)
    vstruct = process_vstruct(vstruct, ["repeat_cell"])
    for element in vstruct["elements"]:
        lattice = [element["cell_vectors"]["a"], element["cell_vectors"]["b"], element["cell_vectors"]["c"]]
        ccoords = [s["ccoord"] for s in element["sites"]]
        cna_jkls = _cna_compute_jkl(ccoords, lattice, min_dist=min_dist, max_dist=max_dist,
                                    max_neighbours=max_neighbours, repeat_cell=repeat_cell)
        cna_cats, cna_colors = _cna_jkl_to_categories(cna_jkls, accuracy=jkl_accuracy, colors=colors)

        for site, cna_cat, cna_color in zip(element["sites"], cna_cats, cna_colors):
            if color_fill:
                site["color_fill"] = cna_color
            if color_outline:
                site["color_outline"] = cna_color
            if merge_label:
                site["label"] = "{0}, {1}".format(site["label"], cna_cat)
            else:
                site["label"] = cna_cat

    return vstruct


color_by_cna.__doc__.format(defaults=dict(_CNA_COLORMAP))
