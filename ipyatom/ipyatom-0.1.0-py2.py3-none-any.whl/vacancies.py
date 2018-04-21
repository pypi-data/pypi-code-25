import numpy as np
from ipyatom import process_vstruct
from ipyatom.geometry3d_utils import transform_to_crystal
from scipy.spatial.ckdtree import cKDTree
import scipy.cluster.hierarchy as hcluster


def compute_vacancies(ccoords, cell, center, grid_spacing=0.2, include_periodic=True,
                      min_dist=3.5, remove_dups=True, ignore_vacuum=None):
    """ compute vacancy positions in a unit cell

    Parameters
    ----------
    ccoords: list or numpy.array((n, 3))
    cell: list or numpy.array((3, 3))
    center: list or numpy.array((3,))
    grid_spacing: float
    include_periodic: bool
        include evaluation of distances to periodic atom images
    min_dist: float
        minimum distance to be considered a vacancy
    remove_dups: bool
        remove duplicate vacancy points (by cluster centering)
    ignore_vacuum: float or None
        if not None, crop the search space in the c-direction to the min/max atomic position +/- ignore_vacuum

    Returns
    -------

    """
    a, b, c = np.asarray(cell)
    origin = np.asarray(center) - 0.5 * (a + b + c)
    ccoords = np.asarray(ccoords)

    if ignore_vacuum is not None:
        fcoords = transform_to_crystal(ccoords, a, b, c, origin)
        cmin, cmax = fcoords[:, 2].min() + ignore_vacuum, fcoords[:, 2].max() - ignore_vacuum
        # TODO this needs to be done more rigourously (get some spurious vacancies at surfaces)
        if cmin < -0.0000001:
            cmin += 1
            cmax += 1
        cmod = abs(cmax - cmin)
        if cmod < 0.1:
            cmax += 0.1
            cmod = abs(cmax - cmin)
        #print(cmin, cmax, cmod)
    else:
        cmin, cmax, cmod = (0., 1., 1.)

    vcoords = []
    for i in np.linspace(0.,  1., int(np.linalg.norm(a)/grid_spacing)):
        for j in np.linspace(0., 1., int(np.linalg.norm(b)/grid_spacing)):
            for k in np.linspace(cmin, cmax, int(cmod*np.linalg.norm(c)/grid_spacing)):
                vcoords.append(origin + i*a + j*b + k*c)

    # repeat coordinates in all direction, where original coordinates are first
    if include_periodic:
        lcoords = np.concatenate((
            ccoords, ccoords - a, ccoords + a))
        lcoords = np.concatenate((
            lcoords, lcoords - b, lcoords + b))
        if not ignore_vacuum:
            lcoords = np.concatenate((
                lcoords, lcoords - c, lcoords + c))
    else:
        lcoords = ccoords.copy()

    # print(lcoords)
    # print()
    # print(len(vcoords))

    # compute nearest neighbours
    ltree = cKDTree(lcoords)
    all_dists, all_ids = ltree.query(vcoords, k=1, distance_upper_bound=min_dist, n_jobs=1)

    vac_list = []
    for vcoord, dist in zip(vcoords, all_dists):
        if np.isinf(dist):
            vac_list.append(vcoord)

    vac_list = np.asarray(vac_list)

    if remove_dups and vac_list.shape[0] > 0:

        # This kind of worked but doesn't find best centre
        # vac_tree = cKDTree(vac_list)
        # pairs = np.asarray(list(vac_tree.query_pairs(min_dist)))
        # if pairs.shape[0] > 0:
        #     #print(np.unique(pairs[:, 0]))
        #     vac_list = np.delete(vac_list, np.unique(pairs[:, 0]), axis=0)

        clusters = hcluster.fclusterdata(vac_list, min_dist, criterion="distance")
        vac_list = np.asarray([np.mean(vac_list[clusters == i], axis=0) for i in set(clusters)])

    return vac_list.tolist()


def add_vacancies(vstruct, grid_spacing=0.2, label="Vac", color="grey", include_periodic=True,
                  min_dist=3.5, elements=None, remove_dups=True, radius=1, transparency=1.,
                  ignore_vacuum=None):
    """

    Parameters
    ----------
    vstruct: dict
    grid_spacing: float
    label: str
        how to label vacancy sites
    color: str or list
    include_periodic: bool
        include evaluation of distances to periodic atom images
    min_dist: float
        minimum distance to be considered a vacancy
    elements: None or list of ints
        if None add to all "repeat_cell" elements
    remove_dups: bool
        remove duplicate vacancy points (by cluster centering)
    radius: float
    transparency: float
        between 0 and 1
    ignore_vacuum: float or None
        if not None, crop the search space in the c-direction to the min/max atomic position +/- ignore_vacuum
    """
    new_vstuct = process_vstruct(vstruct, deepcopy=True)
    for i, element in enumerate(new_vstuct["elements"]):
        if element["type"] != "repeat_cell":
            continue
        if elements is None or i in elements:
            center = element["centre"]
            cell = [element["cell_vectors"][x] for x in "a b c".split()]
            ccoords = [s["ccoord"] for s in element["sites"]]
            vac_coords = compute_vacancies(ccoords, cell, center,
                                           grid_spacing=grid_spacing, include_periodic=include_periodic,
                                           min_dist=min_dist, remove_dups=remove_dups, ignore_vacuum=ignore_vacuum)
            for vac in vac_coords:
                element["sites"].append({
                    'label': label,
                    'ccoord': vac,
                    'cell': [0, 0, 0],
                    'radius': radius,
                    'color_fill': color,
                    'color_outline': None,
                    'transparency': transparency})

    return new_vstuct
