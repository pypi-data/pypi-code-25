"""module to deal with gaussian cube data

NB: for all transformations, the cubes coordinate system is understood to be

A = np.array(
        [[[(x0,y0,z0), (x1,y0,z0)],
          [(x0,y1,z0), (x1,y1,z0)]],
         [[(x0,y0,z1), (x1,y0,z1)],
          [(x0,y1,z1), (x1,y1,z1)]]])

which leads to;
A.shape -> (z length, y length, x length)

or

A.T.shape -> (x length, y length, z length)


"""
from collections import OrderedDict
from itertools import product

import numpy
import numpy as np
import ase
from ipyatomica.visualise.geometry2d_utils import minimum_bounding_box
import ipyatomica.visualise.geometry3d_utils as g3
import pymatgen as pym
from pymatgen.io.ase import AseAtomsAdaptor
from scipy.linalg import expm
from scipy.ndimage import zoom as ndzoom
from scipy.interpolate import interpn
from scipy.spatial.qhull import Delaunay

from jsonschema import validate
from jsonextended import units as eunits
from ipyatomica.visualise.utils import slice_mask, round_to_base, get_default_atom_map
from ipyatomica.visualise.repeat_cell import atoms_to_dict


def gcube_to_dict(cube, cell_vectors, name="", dtype="", vstruct=None, color_bbox="black"):
    """ convert gaussian cube data to visual dict

    Parameters
    ----------
    cube: numpy.array
    cell_vectors: list
        [[a1,a2,a3],[b1,b2,b3],[c1,c2,c3]]
    name: str
        name of structure
    dtype: str
        label of density type (e.g. charge or spin)
    vstruct: dict
        an existing vstruct to append to
    color_bbox: str or None
        color of outline bbox

    Returns
    -------

    """
    a, b, c = cell_vectors
    centre = 0.5 * (np.array(a) + np.array(b) + np.array(c))

    output = {'type': 'repeat_density',
              'name': name,
              'dtype': dtype,
              'centre': centre.tolist(),
              'dcube': cube.copy(),
              'cell_vectors': {"a": a, "b": b, "c": c},
              'color_bbox': color_bbox,
              'transforms': []}

    if vstruct is not None:
        vstruct["elements"].append(output)
        return vstruct
    else:
        return {'elements': [output], 'transforms': []}


def ejdata_to_dict(data, name="", dtype="charge", lunit="angstrom", vstruct=None, color_bbox="black",
                   retrieve_atoms=True, atom_map=None, **kwargs):
    """ convert ejplugin data to visual dict

    Parameters
    ----------
    data: dict
        must contain density and cell_vectors keys
    name: str
        name of structure
    dtype: str
        density type ("charge" or "spin")
    lunit: str
        length unit
    vstruct: dict
        an existing vstruct to append to
    color_bbox: str or None
        color of outline bbox
    retrieve_atoms: bool
        if present retrieve atomic positions as repeat_cell element (requires symbols and fcoords)
    atom_map: None or dict
        a mapping of atom labels to keys; ["radius", "color_fill", "color_outline", "transparency"],
        e.g. {"H": {"radius": 1, "color_fill": '#bfbfbf', "color_outline": None, "transparency": 1.}, ...}
    kwargs : object
        additional per atom parameters (must be lists the same length as number of atoms), e.g. charge=[0,1,-1]

    Returns
    -------

    """
    gkey = "{}_density".format(dtype)
    if gkey not in data or "cell_vectors" not in data:
        raise ValueError("data does not contain both cell_vectors and {} keys".format(gkey))
    validate(data["cell_vectors"], {"type": "object", "required": ["a", "b", "c"],
                                    "properties": {
                                        "a": {"type": "object", "required": ["units", "magnitude"]},
                                        "b": {"type": "object", "required": ["units", "magnitude"]},
                                        "c": {"type": "object", "required": ["units", "magnitude"]}
                                    }})
    cell = eunits.combine_quantities(data["cell_vectors"])
    cell = eunits.apply_unitschema(cell, {"a": lunit, "b": lunit, "c": lunit}, as_quantity=False)
    cell_vectors = [cell["a"].tolist(), cell["b"].tolist(), cell["c"].tolist()]
    output = gcube_to_dict(data[gkey], cell_vectors, name=name, dtype=dtype,
                           vstruct=vstruct, color_bbox=color_bbox)

    if "symbols" in data and "fcoords" in data and retrieve_atoms:
        atoms = ase.Atoms(symbols=data["symbols"], scaled_positions=data["fcoords"], cell=cell_vectors)
        output = atoms_to_dict(atoms, name=name, color_bbox=None, vstruct=output, atom_map=atom_map, **kwargs)
    elif "symbols" in data and "ccoords" in data and retrieve_atoms:
        atoms = ase.Atoms(symbols=data["symbols"], positions=data["ccoords"], cell=cell_vectors)
        output = atoms_to_dict(atoms, name=name, color_bbox=None, vstruct=output, atom_map=atom_map, **kwargs)

    return output


_atom_map_schema = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9]*$": {
            "type": "object",
            "required": ["radius", "color_fill"],
            "properties": {
                "radius": {"type": "number"},
            }
        }

    }
}


def atoms_to_rdensity(atoms, cube_dims=(50, 50, 50), name="", dtype="nuclei", color_bbox="black", vstruct=None,
                      atom_map=None, rdist_implement=2):
    """ convert an atom object to a repeat density

    Parameters
    ----------
    atoms: pymatgen.core.structure.Structure or ase.Atoms
    cube_dims: tuple of int
        (adim, bdim, cdim) of final cube
    name: str
       name of structure
    color_bbox: str or None
        color of outline bbox
    vstruct: dict
        an existing vstruct to append to
    atom_map: None or dict
        a mapping of atom labels to keys; ["radius", "color_fill"],
        e.g. {"H": {"radius": 1, "color_fill": '#bfbfbf'}, ...}
    rdist_implement: int
        implementation for assigning coordinate to atom site (for optimisation testing)

    Returns
    -------
    vstruct: dict
    color_map: dict
        {(<label>, <color>): <value in dcube>, ...}

    """
    if isinstance(atoms, ase.atoms.Atoms):
        atoms = AseAtomsAdaptor.get_structure(atoms)

    if not isinstance(atoms, pym.core.structure.Structure):
        raise ValueError("struct must be ase.Atoms or pymatgen.Structure")

    if vstruct is not None:
        if "elements" not in vstruct:
            raise ValueError("the existing vstruct does not have an elements key")

    # get atom data
    if atom_map is None:
        atom_map = get_default_atom_map()
    validate(atom_map, _atom_map_schema)
    atom_data = atoms.as_dict()
    a, b, c = [_ for _ in atoms.lattice.matrix]
    centre = 0.5 * (a + b + c)
    sites = []
    for i, site in enumerate(atom_data["sites"]):
        label = site["label"]
        site_data = {"ccoord": site["xyz"], "label": label}
        site_data.update(atom_map[label])
        sites.append(site_data)

    # create a map of site labels to color and index
    color_map = {(d[0], d[1]): i + 1 for i, d in enumerate(sorted(
        set([(site["label"], site["color_fill"]) for site in sites])))}

    # create fractional coordinates cube
    ndim, mdim, ldim = cube_dims
    gcube = np.full((ldim, mdim, ndim), np.nan)
    indices = np.array(list(product(range(ldim), range(mdim), range(ndim))))

    # convert indices to cartesian coordinates
    coords = np.einsum('...jk,...k->...j', np.array([a, b, c]).T,
                       np.divide(np.asarray(indices, dtype=np.float64),
                                 np.array((ldim - 1, mdim - 1, ndim - 1), dtype=np.float64))
                       )  # - centre

    # if coord within radial distance of atom set its value

    # TODO time/profile implementations and optimise
    # a) basic for loop implementation
    if rdist_implement == 1:
        for i, coord in enumerate(coords):
            for site in sites:
                if abs(np.linalg.norm(coord - site["ccoord"])) < site["radius"]:
                    gcube[indices[i][0], indices[i][1], indices[i][2]] = color_map[(site["label"], site["color_fill"])]
                    break

    # b) basic numpy implementation
    elif rdist_implement == 2:
        for site in sites:
            mask = np.abs(np.linalg.norm(coords - site["ccoord"], axis=1)) < site["radius"]
            gcube[indices[mask, 0], indices[mask, 1], indices[mask, 2]] = color_map[(site["label"], site["color_fill"])]

    # c) implementation where we avoid computing distances for coordinates already assigned to a site
    # from testing this is actually slower (even for ~100 atom sites)
    elif rdist_implement == 3:
        unassigned_mask = np.full((coords.shape[0],), True)
        for site in sites:
            site_mask = np.full((coords.shape[0],), False)
            site_mask[unassigned_mask] = (np.abs(np.linalg.norm(coords[unassigned_mask] - site["ccoord"], axis=1))
                                          < site["radius"])
            unassigned_mask = np.logical_and(unassigned_mask, np.logical_not(site_mask))
            gcube[indices[site_mask, 0], indices[site_mask, 1], indices[site_mask, 2]] = color_map[(site["label"],
                                                                                                    site["color_fill"])]

    else:
        raise ValueError("rdist_implement must be 1, 2 or 3")

    output = {'type': 'repeat_density',
              'name': name,
              'dtype': dtype,
              'centre': centre.tolist(),
              'dcube': gcube.T,
              'cell_vectors': {"a": a.tolist(), "b": b.tolist(), "c": c.tolist()},
              'color_bbox': color_bbox,
              'transforms': []}

    if vstruct is not None:
        vstruct["elements"].append(output)
        return vstruct, color_map
    else:
        return {'elements': [output], 'transforms': []}, color_map


def _repeat_repeat_density(vstruct, repeats=(0, 0, 0),
                           recentre=True):
    """

    Parameters
    ----------
    vstruct
    repeats
    recentre

    Returns
    -------

    Examples
    --------
    >>> from pprint import pprint
    >>> dstruct = {
    ...  'dcube':np.ones((1,2,3)),
    ...  'centre':[0.5,1.5,2.0],
    ...  'cell_vectors':{
    ...      'a':[1,0,0],
    ...      'b':[0,3,0],
    ...      'c':[0,0,4]}
    ... }
    >>> pprint(dstruct)
    {'cell_vectors': {'a': [1, 0, 0], 'b': [0, 3, 0], 'c': [0, 0, 4]},
     'centre': [0.5, 1.5, 2.0],
     'dcube': array([[[ 1.,  1.,  1.],
            [ 1.,  1.,  1.]]])}

    >>> dstruct["dcube"].shape
    (1, 2, 3)

    >>> _repeat_repeat_density(
    ...     dstruct,(0,1,1))

    >>> dstruct["dcube"].shape
    (2, 4, 3)
    >>> pprint(dstruct)
    {'cell_vectors': {'a': [1.0, 0.0, 0.0],
                      'b': [0.0, 6.0, 0.0],
                      'c': [0.0, 0.0, 8.0]},
     'centre': [0.5, 3.0, 4.0],
     'dcube': array([[[ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.]],
    <BLANKLINE>
           [[ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.]]])}

   """
    rep_a, rep_b, rep_c = repeats
    reps = OrderedDict([('a', 1 + abs(rep_a)), ('b', 1 + abs(rep_b)), ('c', 1 + abs(rep_c))])
    vstruct['dcube'] = np.tile(vstruct['dcube'].T,
                               list(reps.values())).T

    a = np.array(vstruct['cell_vectors']['a'], dtype=float)
    b = np.array(vstruct['cell_vectors']['b'], dtype=float)
    c = np.array(vstruct['cell_vectors']['c'], dtype=float)

    vstruct['cell_vectors'] = {"a": (a * reps["a"]).tolist(),
                               "b": (b * reps["b"]).tolist(),
                               "c": (c * reps["c"]).tolist()}

    if recentre:
        centre = 0.5 * (a * reps["a"] + b * reps["b"] + c * reps["c"])
        vstruct['centre'] = centre.tolist()


def _resize_repeat_density(vstruct, sfraction):
    vstruct['dcube'] = ndzoom(vstruct['dcube'], sfraction)


def _translate_to_repeat_density(vstruct, centre=(0., 0., 0.)):
    vstruct['centre'] = np.asarray(centre, dtype=np.float64).tolist()


def _cslice_repeat_density(dstruct,
                           normal, lbound=None, ubound=None,
                           centre=None):
    """
    Examples
    --------
    >>> from pprint import pprint
    >>> dstruct = {
    ...  'dcube':np.ones((2,4,3)),
    ...  'centre':[1.0,3.0,2.0],
    ...  'cell_vectors':{
    ...      'a':[2.,0,0],
    ...      'b':[0,6.,0],
    ...      'c':[0,0,4.]}
    ... }
    >>> pprint(dstruct)
    {'cell_vectors': {'a': [2.0, 0, 0], 'b': [0, 6.0, 0], 'c': [0, 0, 4.0]},
     'centre': [1.0, 3.0, 2.0],
     'dcube': array([[[ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.]],
    <BLANKLINE>
           [[ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.],
            [ 1.,  1.,  1.]]])}

    >>> dstruct["dcube"].shape
    (2, 4, 3)

    >>> _cslice_repeat_density(
    ...     dstruct,(0,0,1), ubound=3.)
    >>> dstruct["dcube"].shape
    (2, 4, 3)
    >>> pprint(dstruct)
    {'cell_vectors': {'a': [2.0, 0, 0], 'b': [0, 6.0, 0], 'c': [0, 0, 4.0]},
     'centre': [1.0, 3.0, 2.0],
     'dcube': array([[[  1.,   1.,   1.],
            [  1.,   1.,   1.],
            [  1.,   1.,   1.],
            [  1.,   1.,   1.]],
    <BLANKLINE>
           [[ nan,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan]]])}

    >>> _cslice_repeat_density(
    ...     dstruct,(0.,1.,0.), ubound=2.0)
    >>> dstruct["dcube"].shape
    (2, 4, 3)
    >>> pprint(dstruct)
    {'cell_vectors': {'a': [2.0, 0, 0], 'b': [0, 6.0, 0], 'c': [0, 0, 4.0]},
     'centre': [1.0, 3.0, 2.0],
     'dcube': array([[[  1.,   1.,   1.],
            [  1.,   1.,   1.],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan]],
    <BLANKLINE>
           [[ nan,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan]]])}

    >>> _cslice_repeat_density(
    ...     dstruct,(1,0,0), ubound=.9)
    >>> dstruct["dcube"].shape
    (2, 4, 3)
    >>> pprint(dstruct)
    {'cell_vectors': {'a': [2.0, 0, 0], 'b': [0, 6.0, 0], 'c': [0, 0, 4.0]},
     'centre': [1.0, 3.0, 2.0],
     'dcube': array([[[  1.,  nan,  nan],
            [  1.,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan]],
    <BLANKLINE>
           [[ nan,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan],
            [ nan,  nan,  nan]]])}

    >>> dstruct2 = {
    ...  'dcube':np.ones((3,3,3)),
    ...  'centre':[0,0,0],
    ...  'cell_vectors':{
    ...      'a':[2.,0,0],
    ...      'b':[0,2.,0],
    ...      'c':[0,0,2.]}
    ... }
    >>> _cslice_repeat_density(
    ...     dstruct2,(1,1,1), ubound=0)
    >>> dstruct2["dcube"].shape
    (3, 3, 3)
    >>> pprint(dstruct2)
    {'cell_vectors': {'a': [2.0, 0, 0], 'b': [0, 2.0, 0], 'c': [0, 0, 2.0]},
     'centre': [0, 0, 0],
     'dcube': array([[[  1.,   1.,   1.],
            [  1.,   1.,   1.],
            [  1.,   1.,  nan]],
    <BLANKLINE>
           [[  1.,   1.,   1.],
            [  1.,   1.,  nan],
            [  1.,  nan,  nan]],
    <BLANKLINE>
           [[  1.,   1.,  nan],
            [  1.,  nan,  nan],
            [ nan,  nan,  nan]]])}

    """
    normal = np.asarray(normal, dtype=np.float64)
    centre = dstruct['centre'] if centre is None else centre
    a = np.array(dstruct['cell_vectors']['a'], dtype=np.float64)
    b = np.array(dstruct['cell_vectors']['b'], dtype=np.float64)
    c = np.array(dstruct['cell_vectors']['c'], dtype=np.float64)

    cubet = dstruct['dcube'].T

    # get a list of all possible indices
    ldim, mdim, ndim = cubet.shape
    indices = np.array(list(product(range(ldim), range(mdim), range(ndim))), dtype=np.float64)

    # convert them to cartesian coordinates
    coords = np.einsum('...jk,...k->...j', np.array([a, b, c]).T,
                       np.divide(indices, np.array((ldim - 1, mdim - 1, ndim - 1), dtype=np.float64))
                       ) + centre - (a + b + c) / 2.

    # apply slice mask
    mask = slice_mask(coords, normal, lbound, ubound)
    mask = mask.reshape(cubet.shape)
    cubet[~mask] = np.nan
    dstruct['dcube'] = cubet.T


def cube_frac2cart(cvalues, v1, v2, v3, centre=(0., 0., 0.), min_voxels=None, max_voxels=1000000, interp='linear',
                   make_cubic=False, bval=False):
    """convert a 3d cube of values, whose indexes relate to fractional coordinates of v1,v2,v3,
    into a cube of values in the cartesian basis
    (using a background value for coordinates outside the bounding box of v1,v2,v3)

    NB: there may be some edge effects for smaller cubes

    Properties
    ----------
    values : array((N,M,L))
        values in fractional basis
    v1 : array((3,))
    v2 : array((3,))
    v3 : array((3,))
    centre : array((3,))
        cartesian coordinates for centre of v1, v2, v3
    min_voxels : int or None
        minimum number of voxels in returned cube. If None, compute base on input cube
    max_voxels : int or None
        maximum number of voxels in returned cube. If None, compute base on input cube
    interp : str
        interpolation mode; 'nearest' or 'linear'
    make_cubic: bool
        if True, ensure all final cartesian cube sides are of the same length
    bval: float
        background value to use outside the bounding box of the cube.
        If False, use numpy.nan

    Returns
    -------
    B : array((P,Q,R))
        where P,Q,R <= longest_side
    min_bounds : array((3,))
        xmin,ymin,zmin
    max_bounds : array((3,))
        xmax,ymax,zmax

    Example
    -------

    >>> import numpy as np
    >>> fcube = np.array(
    ...    [[[1.,2.],
    ...      [3.,4.]],
    ...     [[5.,6.],
    ...      [7.,8.]]])
    ...
    >>> ncube, min_bound, max_bound = cube_frac2cart(fcube, [1.,0.,0.], [0.,1.,0.], [0.,0.,1.], min_voxels=30)
    >>> min_bound
    array([-0.5, -0.5, -0.5])
    >>> max_bound
    array([ 0.5,  0.5,  0.5])
    >>> ncube.round(1)
    array([[[ 1. ,  1. ,  1.5,  2. ],
            [ 1. ,  1. ,  1.5,  2. ],
            [ 2. ,  2. ,  2.5,  3. ],
            [ 3. ,  3. ,  3.5,  4. ]],
    <BLANKLINE>
           [[ 1. ,  1. ,  1.5,  2. ],
            [ 1. ,  1. ,  1.5,  2. ],
            [ 2. ,  2. ,  2.5,  3. ],
            [ 3. ,  3. ,  3.5,  4. ]],
    <BLANKLINE>
           [[ 3. ,  3. ,  3.5,  4. ],
            [ 3. ,  3. ,  3.5,  4. ],
            [ 4. ,  4. ,  4.5,  5. ],
            [ 5. ,  5. ,  5.5,  6. ]],
    <BLANKLINE>
           [[ 5. ,  5. ,  5.5,  6. ],
            [ 5. ,  5. ,  5.5,  6. ],
            [ 6. ,  6. ,  6.5,  7. ],
            [ 7. ,  7. ,  7.5,  8. ]]])

    >>> ncube, min_bound, max_bound = cube_frac2cart(fcube, [2.,0.,0.], [0.,1.,0.], [0.,0.,1.], min_voxels=30)
    >>> min_bound
    array([-1. , -0.5, -0.5])
    >>> max_bound
    array([ 1. ,  0.5,  0.5])
    >>> ncube.round(1)
    array([[[ 1. ,  1. ,  1.2,  1.5,  1.8,  2. ],
            [ 1.3,  1.3,  1.5,  1.8,  2.2,  2.3],
            [ 2.7,  2.7,  2.8,  3.2,  3.5,  3.7]],
    <BLANKLINE>
           [[ 1.7,  1.7,  1.8,  2.2,  2.5,  2.7],
            [ 2. ,  2. ,  2.2,  2.5,  2.8,  3. ],
            [ 3.3,  3.3,  3.5,  3.8,  4.2,  4.3]],
    <BLANKLINE>
           [[ 4.3,  4.3,  4.5,  4.8,  5.2,  5.3],
            [ 4.7,  4.7,  4.8,  5.2,  5.5,  5.7],
            [ 6. ,  6. ,  6.2,  6.5,  6.8,  7. ]]])

    >>> ncube, min_bound, max_bound = cube_frac2cart(fcube, [1.,0.,0.], [0.,2.,0.], [0.,0.,1.], min_voxels=30)
    >>> min_bound
    array([-0.5, -1. , -0.5])
    >>> max_bound
    array([ 0.5,  1. ,  0.5])
    >>> ncube.round(1)
    array([[[ 1. ,  1.2,  1.8],
            [ 1. ,  1.2,  1.8],
            [ 1.3,  1.5,  2.2],
            [ 2. ,  2.2,  2.8],
            [ 2.7,  2.8,  3.5],
            [ 3. ,  3.2,  3.8]],
    <BLANKLINE>
           [[ 1.7,  1.8,  2.5],
            [ 1.7,  1.8,  2.5],
            [ 2. ,  2.2,  2.8],
            [ 2.7,  2.8,  3.5],
            [ 3.3,  3.5,  4.2],
            [ 3.7,  3.8,  4.5]],
    <BLANKLINE>
           [[ 4.3,  4.5,  5.2],
            [ 4.3,  4.5,  5.2],
            [ 4.7,  4.8,  5.5],
            [ 5.3,  5.5,  6.2],
            [ 6. ,  6.2,  6.8],
            [ 6.3,  6.5,  7.2]]])

     >>> ncube, min_bound, max_bound = cube_frac2cart(fcube, [1.,0.,0.], [0.,1.,0.], [0.,0.,2.], min_voxels=30)
    >>> min_bound
    array([-0.5, -0.5, -1. ])
    >>> max_bound
    array([ 0.5,  0.5,  1. ])
    >>> ncube.round(1)
    array([[[ 1. ,  1.2,  1.8],
            [ 1.3,  1.5,  2.2],
            [ 2.7,  2.8,  3.5]],
    <BLANKLINE>
           [[ 1. ,  1.2,  1.8],
            [ 1.3,  1.5,  2.2],
            [ 2.7,  2.8,  3.5]],
    <BLANKLINE>
           [[ 1.7,  1.8,  2.5],
            [ 2. ,  2.2,  2.8],
            [ 3.3,  3.5,  4.2]],
    <BLANKLINE>
           [[ 3. ,  3.2,  3.8],
            [ 3.3,  3.5,  4.2],
            [ 4.7,  4.8,  5.5]],
    <BLANKLINE>
           [[ 4.3,  4.5,  5.2],
            [ 4.7,  4.8,  5.5],
            [ 6. ,  6.2,  6.8]],
    <BLANKLINE>
           [[ 5. ,  5.2,  5.8],
            [ 5.3,  5.5,  6.2],
            [ 6.7,  6.8,  7.5]]])

     >>> ncube, min_bound, max_bound = cube_frac2cart(fcube, [1.,0.,0.], [.7,.7,0.], [0.,0.,1.], min_voxels=30)
    >>> min_bound
    array([-0.85, -0.35, -0.5 ])
    >>> max_bound
    array([ 0.85,  0.35,  0.5 ])
    >>> ncube.round(1)
    array([[[ 1. ,  1.1,  1.6,  2. ,  nan,  nan],
            [ nan,  nan,  2. ,  2.5,  3. ,  nan]],
    <BLANKLINE>
           [[ 1.7,  1.7,  2.3,  2.7,  nan,  nan],
            [ nan,  nan,  2.7,  3.2,  3.7,  nan]],
    <BLANKLINE>
           [[ 4.3,  4.4,  5. ,  5.3,  nan,  nan],
            [ nan,  nan,  5.3,  5.8,  6.3,  nan]]])

   >>> ncube, min_bound, max_bound = cube_frac2cart(fcube, [2.,0.,0.], [0.,1.,0.], [0.,0.,1.], min_voxels=30, make_cubic=True)
    >>> min_bound
    array([-1. , -0.5, -0.5])
    >>> max_bound
    array([ 1. ,  1.5,  1.5])
    >>> ncube.round(1)
    array([[[ 1. ,  1. ,  1.5,  2. ],
            [ 2. ,  2. ,  2.5,  3. ],
            [ 3. ,  3. ,  3.5,  4. ],
            [ nan,  nan,  nan,  nan]],
    <BLANKLINE>
           [[ 3. ,  3. ,  3.5,  4. ],
            [ 4. ,  4. ,  4.5,  5. ],
            [ 5. ,  5. ,  5.5,  6. ],
            [ nan,  nan,  nan,  nan]],
    <BLANKLINE>
           [[ 5. ,  5. ,  5.5,  6. ],
            [ 6. ,  6. ,  6.5,  7. ],
            [ 7. ,  7. ,  7.5,  8. ],
            [ nan,  nan,  nan,  nan]],
    <BLANKLINE>
           [[ nan,  nan,  nan,  nan],
            [ nan,  nan,  nan,  nan],
            [ nan,  nan,  nan,  nan],
            [ nan,  nan,  nan,  nan]]])

   """
    cvalues = np.asarray(cvalues, dtype=float).T

    min_voxels = min_voxels if min_voxels is not None else 1
    longest_side = max(cvalues.shape)
    if (min_voxels is not None) and (max_voxels is not None) and min_voxels > max_voxels:
        raise ValueError(
            "minimum dimension ({0}) must be less than or equal to maximum distance ({1})".format(min_voxels,
                                                                                                  max_voxels))
    if min_voxels is not None:
        longest_side = max(longest_side, int(min_voxels ** (1 / 3.)))
    if max_voxels is not None:
        longest_side = min(longest_side, int(max_voxels ** (1 / 3.)))

    # convert to numpy arrays
    origin = np.asarray([0, 0, 0], dtype=float)
    v1 = np.asarray(v1)
    v2 = np.asarray(v2)
    v3 = np.asarray(v3)

    # --------------
    # expand cube by one unit in all directions (for interpolation)
    cvalues = np.concatenate((np.array(cvalues[0], ndmin=3), cvalues, np.array(cvalues[-1], ndmin=3)), axis=0)
    start = np.transpose(np.array(cvalues[:, :, 0], ndmin=3), axes=[1, 2, 0])
    end = np.transpose(np.array(cvalues[:, :, -1], ndmin=3), axes=[1, 2, 0])
    cvalues = np.concatenate((start, cvalues, end), axis=2)
    start = np.transpose(np.array(cvalues[:, 0, :], ndmin=3), axes=[1, 0, 2])
    end = np.transpose(np.array(cvalues[:, -1, :], ndmin=3), axes=[1, 0, 2])
    cvalues = np.concatenate((start, cvalues, end), axis=1)
    # --------------

    # --------------
    # create fractional coordinate axes for cube
    f_axes = []
    for i, v in enumerate([v1, v2, v3]):
        step = 1. / (cvalues.shape[i] - 2.)
        ax = np.linspace(0, 1 + step, cvalues.shape[i]) - step / 2.
        f_axes.append(ax)
    # --------------

    # --------------
    # get bounding box for cartesian vectors and compute its volume and extents
    bbox_pts = np.asarray([origin, v1, v2, v3, v1 + v2, v1 + v3, v1 + v2 + v3, v2 + v3])
    hull = Delaunay(bbox_pts)
    bbox_x, bbox_y, bbox_z = bbox_pts.T
    xmin, xmax, ymin, ymax, zmin, zmax = (bbox_x.min(), bbox_x.max(), bbox_y.min(),
                                          bbox_y.max(), bbox_z.min(), bbox_z.max())  # l,r,bottom,top
    x_length = abs(xmin - xmax)
    y_length = abs(ymin - ymax)
    z_length = abs(zmin - zmax)
    if make_cubic:
        # min_bound, max_bound = min(xmin, ymin, zmin), max(xmax, ymax, zmin)
        max_length = max(x_length, y_length, z_length)
        xmax += max_length - (xmin + x_length)
        ymax += max_length - (ymin + y_length)
        zmax += max_length - (zmin + z_length)
        x_length = y_length = z_length = max_length

    # --------------

    # --------------
    # compute new cube size, in which the bounding box can fit
    xlen, ylen, zlen = 0, 0, 0
    while xlen * ylen * zlen < min_voxels:
        if x_length == max([x_length, y_length, z_length]):
            xlen = longest_side
            ylen = int(longest_side * y_length / float(x_length))
            zlen = int(longest_side * z_length / float(x_length))
        elif y_length == max([x_length, y_length, z_length]):
            ylen = longest_side
            xlen = int(longest_side * x_length / float(y_length))
            zlen = int(longest_side * z_length / float(y_length))
        else:
            zlen = longest_side
            xlen = int(longest_side * x_length / float(z_length))
            ylen = int(longest_side * y_length / float(z_length))
        longest_side += 1
    # --------------

    # --------------
    # create a new, initially empty cube
    new_array = np.full((xlen, ylen, zlen), bval if bval is not False else np.nan)
    # get the indexes for each voxel in cube
    xidx, yidx, zidx = np.meshgrid(range(new_array.shape[0]), range(new_array.shape[1]), range(new_array.shape[2]))
    xidx = xidx.flatten()
    yidx = yidx.flatten()
    zidx = zidx.flatten()
    xyzidx = np.concatenate((np.array(xidx, ndmin=2).T, np.array(yidx, ndmin=2).T, np.array(zidx, ndmin=2).T), axis=1)
    # --------------

    # --------------
    # get the cartesian coordinates for each voxel
    xyz = np.concatenate((np.array(xmin + (xyzidx[:, 0] * abs(xmin - xmax) / float(xlen)), ndmin=2).T,
                          np.array(ymin + (xyzidx[:, 1] * abs(ymin - ymax) / float(ylen)), ndmin=2).T,
                          np.array(zmin + (xyzidx[:, 2] * abs(zmin - zmax) / float(zlen)), ndmin=2).T), axis=1)
    # create a mask for filtering all cartesian coordinates which sit inside the bounding box
    inside_mask = hull.find_simplex(xyz) >= 0
    # --------------

    # --------------
    # for all coordinates inside the bounding box, get their equivalent fractional position and set intepolated value
    basis_transform = np.linalg.inv(np.transpose([v1, v2, v3]))
    uvw = np.einsum('...jk,...k->...j', basis_transform, xyz[inside_mask])
    mask_i, mask_j, mask_k = xyzidx[inside_mask][:, 0], xyzidx[inside_mask][:, 1], xyzidx[inside_mask][:, 2]
    new_array[mask_i, mask_j, mask_k] = interpn(f_axes, cvalues, uvw, bounds_error=True, method=interp)
    # --------------

    mins = np.array((xmin, ymin, ymin)) - 0.5 * (v1 + v2 + v3) + np.array(centre)
    maxes = np.array((xmax, ymax, zmax)) - 0.5 * (v1 + v2 + v3) + np.array(centre)
    return new_array.T, mins, maxes


def sliceplane_points(cbounds, scentre, snormal, cell_size=None, orientation=None, alter_bbox=(0., 0., 0., 0.),
                      angle_step=1., dist_tol=1e-5):
    """ get a 2d array of points for a cartesian cube slice on an arbitrary plane

    1. A minimum rectangular bounding box is found on the plane which encpasulates the whole of carray.
    2. The bbox is discretised (by cell_size) and a value obtained (by interpolation) at each point
       (points outside carray are set at numpy.nan).
    3. Finally the point coordinates are transformed onto a 2d x-y plane

    Parameters
    ----------
    cbounds: Tuple
        bounds of carray: (xmin, xmax, ymin, ymax, zmin, zmax)
    scentre: Tuple
        point on slice plane (x, y, z)
    snormal: Tuple
        norma of slice plane (x, y, z)
    cell_size: float
        length of discretised cells. If None, cell_size = <minimum cube length> * 0.01
    orientation: int or None
        between 0 and 3, select a specific bbox orientation (rotated by orientation * 90 degrees)
        if None, the orientation is selected such that corner min(x',y') -> min(x,y,z)
    alter_bbox: tuple of floats
        move edges of computed bbox (bottom, top, left, right)
    angle_step: float
        angular step (degrees) for mapping plane intersection with bounding box
    dist_tol: float
        distance tolerance for finding edge of bounding box

    Returns
    -------
    corners: list of tuples
        corners of bounding box in original coordinates: [bottom left, bottom right, top left, top right]
    corners_xy: list of tuples
        corners of bounding box in 2d projections: [bottom left, bottom right, top left, top right]
    gpoints: numpy.array
        list of (x, y, z) in real space
    gpoints_xy: numpy.array
        list of (x, y) in 2d projection

    Examples
    --------
    >>> import numpy as np
    >>> cbounds = (0., 1., 0., 1., 0., 1.)
    >>> corners, corners_xy, gpoints, gpoints_xy = sliceplane_points(cbounds, (0.5, 0.5, .5), (0., 0., 1.),
    ...                                                  cell_size=.25, alter_bbox=(.001, 0., .001, 0.))
    >>> np.array(corners).round(2).tolist()
    [[0.0, 0.0, 0.5], [1.0, 0.0, 0.5], [0.0, 1.0, 0.5], [1.0, 1.0, 0.5]]
    >>> np.array(corners_xy).round(2).tolist()
    [[-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]]
    >>> gpoints.round(2)
    array([[ 0.  ,  0.  ,  0.5 ],
           [ 0.  ,  0.25,  0.5 ],
           [ 0.  ,  0.5 ,  0.5 ],
           [ 0.  ,  0.75,  0.5 ],
           [ 0.25,  0.  ,  0.5 ],
           [ 0.25,  0.25,  0.5 ],
           [ 0.25,  0.5 ,  0.5 ],
           [ 0.25,  0.75,  0.5 ],
           [ 0.5 ,  0.  ,  0.5 ],
           [ 0.5 ,  0.25,  0.5 ],
           [ 0.5 ,  0.5 ,  0.5 ],
           [ 0.5 ,  0.75,  0.5 ],
           [ 0.75,  0.  ,  0.5 ],
           [ 0.75,  0.25,  0.5 ],
           [ 0.75,  0.5 ,  0.5 ],
           [ 0.75,  0.75,  0.5 ]])
    >>> gpoints_xy.round(2)
    array([[-0.5 , -0.5 ],
           [-0.5 , -0.25],
           [-0.5 ,  0.  ],
           [-0.5 ,  0.25],
           [-0.25, -0.5 ],
           [-0.25, -0.25],
           [-0.25,  0.  ],
           [-0.25,  0.25],
           [ 0.  , -0.5 ],
           [ 0.  , -0.25],
           [ 0.  ,  0.  ],
           [ 0.  ,  0.25],
           [ 0.25, -0.5 ],
           [ 0.25, -0.25],
           [ 0.25,  0.  ],
           [ 0.25,  0.25]])

    """
    # 1. assert that scentre is within the cube bounds
    xmin, xmax, ymin, ymax, zmin, zmax = cbounds
    x0, y0, z0 = scentre
    if not (xmin < x0 < xmax):
        raise ValueError("scentre x must be within the cube bounds")
    if not (ymin < y0 < ymax):
        raise ValueError("scentre y must be within the cube bounds")
    if not (zmin < z0 < zmax):
        raise ValueError("scentre z must be within the cube bounds")

    # 2. find the equation of the plane a.x + b.y + c.z = d
    a, b, c = snormal
    if a == 0 and b == 0 and c == 0:
        raise ValueError("snormal cannot be (0, 0, 0)")
    d = a * x0 + b * y0 + c * z0

    # 3. find another point on the plane
    if c == 0:  # z can equal anything
        z1 = z0 + .1
        if b == 0:  # y can equal anything
            y1 = y0 + .1
            x1 = d / float(a)
        elif a == 0:  # x can equal anything
            x1 = x0 + .1
            y1 = d / float(b)
        else:
            y1 = d / float(b)
            x1 = (d - b * y1) / float(a)
    else:
        x1 = x0 + .1
        y1 = y0 + .1
        z1 = (d - (a * x1 + b * y1)) / float(c)

    scentre = np.asarray((x0, y0, z0), dtype=float)
    spoint = np.asarray((x1, y1, z1), dtype=float)

    # 4. map out points of intersection between the plane and bounding box by scanning radially around scentre
    # TODO max while loop iterations, to avoid infinite loops
    def inside_box(point):
        x, y, z = point
        return (xmin < x < xmax) and (ymin < y < ymax) and (zmin < z < zmax)

    bpoints = []
    for angle in np.arange(0, 360, angle_step):
        # 4.1 rotate spoint around snormal (at scentre) to get new point
        p1 = np.dot(expm(np.cross(np.eye(3), snormal / np.linalg.norm(snormal) * np.radians(angle))),
                    spoint - scentre) + scentre

        # 4.2 find two points on the line which are either side of the cubes bounding box and along the line scentre->p1
        if inside_box(p1):
            p2 = (p1 - scentre) * 2. + scentre
            while inside_box(p2):
                p2 = (p2 - scentre) * 2. + scentre
        else:
            p3 = (p1 - scentre) * .5 + scentre
            while not inside_box(p3):
                p3 = (p3 - scentre) * .5 + scentre
            p2 = p1.copy()
            p1 = p3.copy()

        # 4.3 move the points closer together until a required distance apart
        dist = np.linalg.norm(p1 - p2)
        while dist > dist_tol:
            if inside_box(p1 + .5 * (p2 - p1)):
                p1 = p1 + .5 * (p2 - p1)
            else:
                p2 = p2 - .5 * (p2 - p1)
            dist = np.linalg.norm(p1 - p2)
        bpoints.append(p1 + .5 * (p2 - p1))

    # 5. transform the points on to a 2D x-y plane (i.e. snormal -> (0,0,1))
    rmatrix = g3.align_rotation_matrix(snormal, [0, 0, 1], point=scentre)
    xy_vectors = g3.apply_transform(bpoints, rmatrix)[:, 0:2]
    plane_z = scentre[2]

    # 6. Find the minimum 2D rectangle encompassing all of the transformed points
    bbox = minimum_bounding_box(xy_vectors)
    corners = np.zeros((4, 3))
    corners[:, :2] = bbox.corner_points

    # 7. transform the rectangle, such that its centre is at [0,0,0] and its edges are parallel to [1,0,0] and [0,1,0]
    #    if orientation is None, orientate bbox so that bottom left corner corresponds to min(x,y,z) point in real space
    tmatrix2 = g3.translation_matrix(np.array([-bbox.rectangle_center[0], -bbox.rectangle_center[1], -plane_z]))
    corners_xy = g3.apply_transform(corners, tmatrix2)
    bottom, top, left, right = alter_bbox

    orientation_map = {0: 0., 1: np.pi / 2., 2: np.pi, 3: 3. * np.pi / 2.}
    if orientation is not None:
        orientation_map = {orientation: orientation_map[orientation]}

    best_orientation = None
    for oid, orot in orientation_map.items():
        rmatrix2 = g3.rotation_matrix(bbox.unit_vector_angle + orot, (0., 0., 1.))
        corners = g3.apply_transform(corners_xy.copy(), rmatrix2)
        bottom_left_xy = (corners[:, 0].min() + left, corners[:, 1].min() + bottom, 0.)

        inv_transform = g3.concatenate_matrices(g3.inverse_matrix(rmatrix),
                                                g3.inverse_matrix(tmatrix2),
                                                g3.inverse_matrix(rmatrix2))
        bottom_left = g3.apply_transform([bottom_left_xy], inv_transform)[0]

        if best_orientation is None:
            best_orientation = {"bl": bottom_left, "rmatrix2": rmatrix2, "corners": corners}
        else:
            if round_to_base(bottom_left[2], dist_tol) < round_to_base(best_orientation["bl"][2], dist_tol):
                best_orientation = {"bl": bottom_left, "rmatrix2": rmatrix2, "corners": corners}
            elif round_to_base(bottom_left[2], dist_tol) == round_to_base(best_orientation["bl"][2], dist_tol):
                if round_to_base(bottom_left[1], dist_tol) < round_to_base(best_orientation["bl"][1], dist_tol):
                    best_orientation = {"bl": bottom_left, "rmatrix2": rmatrix2, "corners": corners}
                elif round_to_base(bottom_left[1], dist_tol) == round_to_base(best_orientation["bl"][1], dist_tol):
                    if round_to_base(bottom_left[0], dist_tol) < round_to_base(best_orientation["bl"][0], dist_tol):
                        best_orientation = {"bl": bottom_left, "rmatrix2": rmatrix2, "corners": corners}

    rmatrix2 = best_orientation["rmatrix2"]
    corners = best_orientation["corners"]

    corners_xy = np.array([(corners[:, 0].min() + left, corners[:, 1].min() + bottom, 0.),  # bottom left
                           (corners[:, 0].max() + right, corners[:, 1].min() + bottom, 0.),  # bottom right
                           (corners[:, 0].min() + left, corners[:, 1].max() + top, 0.),  # top left
                           (corners[:, 0].max() + right, corners[:, 1].max() + top, 0.)],  # top right
                          dtype=np.float64)

    # 8. create a grid of points with the required discretisation
    if cell_size is None:
        cell_size = min([abs(xmin - xmax), abs(ymin - ymax), abs(zmin - zmax)]) * 0.01
    gpoints_xy = np.array(list(product(
        np.arange(corners[:, 0].min() + left, corners[:, 0].max() + right, cell_size),
        np.arange(corners[:, 1].min() + bottom, corners[:, 1].max() + top, cell_size))))
    gpoints = np.zeros((gpoints_xy.shape[0], 3))
    gpoints[:, :2] = gpoints_xy

    # 9. transform the points back onto the original plane
    inv_transform = g3.concatenate_matrices(g3.inverse_matrix(rmatrix),
                                            g3.inverse_matrix(tmatrix2),
                                            g3.inverse_matrix(rmatrix2))

    corners = g3.apply_transform(corners_xy, inv_transform).tolist()
    corners_xy = corners_xy[:, :2].tolist()
    gpoints = g3.apply_transform(gpoints, inv_transform)

    return corners, corners_xy, gpoints, gpoints_xy


def cubesliceplane(carray, cbounds, scentre, snormal, cell_size=None, orientation=None, alter_bbox=(0., 0., 0., 0.),
                   bval=np.nan, angle_step=1., dist_tol=1e-5):
    """ get a 2d array of values for a cartesian cube slice on an arbitrary plane

    1. A minimum rectangular bounding box is found on the plane which encpasulates the whole of carray.
    2. The bbox is discretised (by cell_size) and a value obtained (by interpolation) at each point
       (points outside carray are set at numpy.nan).
    3. The point coordinates are transformed onto a 2d x-y plane
    4. Finally interpolate into the cube to get values at each grid point

    NB: due to rounding errors, some points along the edge of carray may lie just outside it and be set as numpy.nan

    Parameters
    ----------
    carray: numpr.array
        array of values
    cbounds: Tuple
        bounds of carray: (xmin, xmax, ymin, ymax, zmin, zmax)
    scentre: Tuple
        point on slice plane (x, y, z)
    snormal: Tuple
        norma of slice plane (x, y, z)
    cell_size: float
        length of discretised cells. If None, cell_size = <minimum cube length> * 0.01
    orientation: int or None
        between 0 and 3, select a specific bbox orientation (rotated by orientation * 90 degrees)
        if None, the orientation is selected such that corner min(x',y') -> min(x,y,z)
    alter_bbox: tuple of floats
        move edges of computed bbox (bottom, top, left, right)
    angle_step: float
        angular step (degrees) for mapping plane intersection with bounding box
    dist_tol: float
        distance tolerance for finding edge of bounding box

    Returns
    -------
    corners: list of tuples
        corners of bounding box in original coordinates: [bottom left, bottom right, top left, top right]
    corners_xy: list of tuples
        corners of bounding box in 2d projections: [bottom left, bottom right, top left, top right]
    gvalues_xy: numpy.array
        list of (x, y, value) in 2d projections

    Examples
    --------
    >>> import numpy as np
    >>> ccube = np.array([
    ...     [[1.,1.,1.],
    ...      [1.,1.,1.],
    ...      [1.,1.,1.]],
    ...     [[2.,3.,4.],
    ...      [2.,3.,4.],
    ...      [2.,3.,4.]],
    ...     [[5.,5.,5.],
    ...      [5.,5.,5.],
    ...      [5.,5.,5.]]])
    ...
    >>> cbounds = (0., 1., 0., 1., 0., 1.)
    >>> corners, corners_xy, gvalues_xy = cubesliceplane(ccube, cbounds, (0.5, 0.5, .5), (0., 0., 1.),
    ...                                                  cell_size=.25, alter_bbox=(.001, 0., .001, 0.))
    >>> np.array(corners).round(2).tolist()
    [[0.0, 0.0, 0.5], [1.0, 0.0, 0.5], [0.0, 1.0, 0.5], [1.0, 1.0, 0.5]]
    >>> np.array(corners_xy).round(2).tolist()
    [[-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]]
    >>> gvalues_xy.round(2)
    array([[-0.5 , -0.5 ,  2.  ],
           [-0.5 , -0.25,  2.  ],
           [-0.5 ,  0.  ,  2.  ],
           [-0.5 ,  0.25,  2.  ],
           [-0.25, -0.5 ,  2.5 ],
           [-0.25, -0.25,  2.5 ],
           [-0.25,  0.  ,  2.5 ],
           [-0.25,  0.25,  2.5 ],
           [ 0.  , -0.5 ,  3.  ],
           [ 0.  , -0.25,  3.  ],
           [ 0.  ,  0.  ,  3.  ],
           [ 0.  ,  0.25,  3.  ],
           [ 0.25, -0.5 ,  3.5 ],
           [ 0.25, -0.25,  3.5 ],
           [ 0.25,  0.  ,  3.5 ],
           [ 0.25,  0.25,  3.5 ]])

    """
    xmin, xmax, ymin, ymax, zmin, zmax = cbounds
    outputs = sliceplane_points(cbounds, scentre, snormal, cell_size=cell_size, orientation=orientation,
                                alter_bbox=alter_bbox, angle_step=angle_step, dist_tol=dist_tol)
    corners, corners_xy, gpoints, gpoints_xy = outputs

    # interpolate into the cube to get values at each grid point
    cvalues = carray.T
    gvalues = interpn([np.linspace(xmin, xmax, cvalues.shape[0]),
                       np.linspace(ymin, ymax, cvalues.shape[1]),
                       np.linspace(zmin, zmax, cvalues.shape[2])],
                      cvalues, gpoints, method="linear", bounds_error=False, fill_value=bval)

    gvalues = np.array(gvalues, ndmin=2, copy=False).T

    return corners, corners_xy, np.concatenate([gpoints_xy, gvalues], axis=1)


if __name__ == "__main__":

    from pprint import pprint

    if True:
        from ase.build import bulk as ase_bulk
        from ase.atoms import Atoms

        # input1 = bulk("Fe").repeat((1, 1, 1))
        # atoms = Atoms(symbols=["Fe", "S"], scaled_positions=[[0.25, 0.25, 0.25], [0.75, 0.75, 0.75]],
        #               cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        atoms = ase_bulk("Fe")
        print(atoms.get_positions())
        atom_map = {"Fe": {"radius": 1.3, "color_fill": "red"}, "S": {"radius": .5, "color_fill": "blue"}}
        dstruct, c_map = atoms_to_rdensity(atoms, cube_dims=(5, 5, 5), atom_map=atom_map)
        pprint(c_map)
        pprint(dstruct["elements"][0]["cell_vectors"])
        print(dstruct["elements"][0]["centre"])
        pprint(dstruct["elements"][0]["dcube"].tolist())

    if False:
        from ase.build import bulk
        from ipyatomica.iron_sulfide_params import get_fes_bulk

        input2 = get_fes_bulk("mackinawite")
        print(input2)
        dstruct, c_map = atoms_to_rdensity(input2, cube_dims=(200, 200, 200))
        print(c_map)
        # print(dstruct["elements"][0]["dcube"])
        ccube, mins1, maxs1 = cube_frac2cart(dstruct["elements"][0]["dcube"],
                                             dstruct["elements"][0]["cell_vectors"]["a"],
                                             dstruct["elements"][0]["cell_vectors"]["b"],
                                             dstruct["elements"][0]["cell_vectors"]["c"], interp="nearest")
        print(np.unique(dstruct["elements"][0]["dcube"].astype(int), return_counts=True))
        print(np.unique(ccube.astype(int), return_counts=True))

    if False:
        import timeit

        times = {}
        for rdist_imp in [2, 3]:
            for cdim in [25, 50, 75, 100]:
                for adim in [1, 2, 3, 4]:
                    times[(rdist_imp, cdim, adim)] = min(timeit.repeat(
                        "atoms_to_rdensity(bulk_fe, cube_dims=({0},{0},{0}), rdist_implement={1})".format(cdim,
                                                                                                          rdist_imp),
                        setup="""
                        from ipyatomica.visualise.repeat_density import atoms_to_rdensity
                        from ase.build import bulk
                        bulk_fe = bulk("Fe")
                        bulk_fe = bulk_fe.repeat(({0},{0},{0}))
                                """.replace("  ", "").format(adim), repeat=3, number=1))

        pprint(times)
