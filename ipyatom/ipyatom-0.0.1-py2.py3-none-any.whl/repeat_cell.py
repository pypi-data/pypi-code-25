import copy
import warnings
import numpy as np
import ase
from ipyatomica.visualise.utils import slice_mask, get_default_atom_map
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from jsonschema import validate

from jsonextended import edict
from jsonextended import units as eunits
from ipyatomica.visualise.validation import process_vstruct

with warnings.catch_warnings(record=True):
    warnings.filterwarnings("ignore", category=ImportWarning)
    import pymatgen as pym
    from pymatgen.io.ase import AseAtomsAdaptor


_atom_map_schema = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9]*$": {
            "type": "object",
            "required": ["radius", "color_fill", "color_outline", "transparency"],
            "properties": {
                "radius": {"type": "number"},
                "transparency": {"type": "number", "minimum": 0., "maximum": 1.}
            }
        }

    }
}


def atoms_to_dict(atoms, name="", color_bbox="black", vstruct=None, atom_map=None, **kwargs):
    """ convert an atom object to a dict

    Parameters
    ----------
    atoms: pymatgen.core.structure.Structure or ase.Atoms
    name: str
    color_bbox: str or None
        color of outline bbox
    vstruct: dict
        an existing vstruct to append to
    atom_map: None or dict
        a mapping of atom labels to keys; ["radius", "color_fill", "color_outline", "transparency"],
        e.g. {"H": {"radius": 1, "color_fill": '#bfbfbf', "color_outline": None, "transparency": 1.}, ...}
    kwargs : object
        additional per atom parameters (must be lists the same length as number of atoms), e.g. charge=[0,1,-1]

    Returns
    -------

    """
    if isinstance(atoms, ase.atoms.Atoms):
        atoms = AseAtomsAdaptor.get_structure(atoms)

    if not isinstance(atoms, pym.core.structure.Structure):
        raise ValueError("struct must be ase.Atoms or pymatgen.Structure")

    if atom_map is None:
        atom_map = get_default_atom_map()
    validate(atom_map, _atom_map_schema)
    atom_data = atoms.as_dict()

    if vstruct is not None:
        if "elements" not in vstruct:
            raise ValueError("the existing vstruct does not have an elements key")

    for k, v in kwargs.items():
        if k in ["radius", "color_fill", "color_outline", "transparency", "label"]:
            raise ValueError("keyword argument {} cannot be named; ".format(k)
                             + "radius, color_fill, color_outline, transparency or label")
        if len(v) != len(atom_data["sites"]):
            raise ValueError("the keyword argument {0}'s value must be a list "
                             "the same length as the number of atoms ({1})".format(k, len(atom_data["sites"])))

    # color = 'rgb({r},{g},{b})'
    a, b, c = [_ for _ in atoms.lattice.matrix]
    centre = 0.5 * (a + b + c)

    sites = []
    for i, site in enumerate(atom_data["sites"]):
        # TODO better way of addressing label/elements (as in pymatgen)
        label = site["species"][0]["element"]
        site_data = {
            "ccoord": site["xyz"],
            # "fcoord": site["abc"],
            "label": label,
            # "color_fill": atom_map[label]["color_fill"],
            # "color_outline": atom_map[label]["color_outline"],
            # "radius": atom_map[label]["radius"],
            # "transparency": atom_map[label]["transparency"],
            "cell": [0, 0, 0]
        }
        site_data.update(atom_map[label])
        site_data.update({k: v[i] for k, v in kwargs.items()})
        sites.append(site_data)

    output = {
        "type": "repeat_cell",
        "name": name,
        "centre": centre.tolist(),
        "color_bbox": color_bbox,
        "cell_vectors": {
            "a": a.tolist(),
            "b": b.tolist(),
            "c": c.tolist()
        },
        "sites": sites,
        "bonds": [],
        "transforms": [],
    }
    if vstruct is not None:
        vstruct["elements"].append(output)
        return vstruct
    else:
        return {'elements': [output], 'transforms': []}


def ejdata_to_dict(ejdata, name="", lunit="angstrom", color_bbox="black", vstruct=None, atom_map=None, **kwargs):
    """ convert an ejdata type to a dict

    Parameters
    ----------
    ejdata: dict
        requires keys: atomic_numbers or symbols, fcoords or ccoords, cell_parameters or cell_vectors
    name: str
    lunit: str
        length unit
    color_bbox: str or None
        color of outline bbox
    vstruct: dict
        an existing vstruct to append to
    atom_map: None or dict
        a mapping of atom labels to keys; ["radius", "color_fill", "color_outline", "transparency"],
        e.g. {"H": {"radius": 1, "color_fill": '#bfbfbf', "color_outline": None, "transparency": 1.}, ...}
    kwargs : object
        additional per atom parameters (must be lists the same length as number of atoms), e.g. charge=[0,1,-1]

    Returns
    -------

    """
    params = {}
    ejdata = eunits.combine_quantities(ejdata)
    ejdata = eunits.apply_unitschema(ejdata, {"ccoords": lunit,
                                              "a": lunit, "b": lunit, "c": lunit,
                                              "alpha": "degrees", "beta": "degrees", "gamma": "degrees"},
                                     as_quantity=False)

    if "atomic_numbers" in ejdata:
        params["numbers"] = np.asarray(ejdata["atomic_numbers"]).tolist()
    elif "symbols" in ejdata:
        params["symbols"] = np.asarray(ejdata["symbols"]).tolist()
    else:
        raise ValueError("requires one of key 'atomic_numbers' or 'symbols'")

    if "fcoords" in ejdata:
        params["scaled_positions"] = np.asarray(ejdata["fcoords"]).tolist()
    elif "ccoords" in ejdata:
        params["positions"] = np.asarray(ejdata["ccoords"]).tolist()
    else:
        raise ValueError("requires one of key 'fcoords' or 'ccoords'")

    if "cell_vectors" in ejdata:
        params["cell"] = [np.asarray(ejdata["cell_vectors"][k]).tolist() for k in ["a", "b", "c"]]
    elif "cell_parameters" in ejdata:
        params["cell"] = [ejdata["cell_parameters"][k] for k in ["a", "b", "c", "alpha", "beta", "gamma"]]
    else:
        raise ValueError("requires one of key 'cell_parameters' or 'cell_vectors'")

    atoms = ase.Atoms(**params)
    return atoms_to_dict(atoms, name=name, color_bbox=color_bbox, vstruct=vstruct, atom_map=atom_map, **kwargs)


def change_site_variable(vstruct, changes, filters=None, deepcopy=True):
    """

    Parameters
    ----------
    vstruct: dict
    changes: dict
        changes to make to site, e.g. {"radius": 1}
    filters: dict
        apply change only if all filters are met, e.g. {"label": "Fe"}
    deepcopy:
        deepcopy structure before altering

    Returns
    -------

    """
    vstruct = process_vstruct(vstruct, ["repeat_cell"], deepcopy=deepcopy)
    for element in vstruct["elements"]:
        for site in element["sites"]:
            filters_ok = True
            if filters is not None:
                for k, v in filters.items():
                    if k not in site:
                        filters_ok = False
                    elif site[k] != v:
                        filters_ok = False
            if filters_ok:
                for k2, v2 in changes.items():
                    site[k2] = v2
    return vstruct


def filter_sites(vstruct, filter_by, allowed, deepcopy=True):
    """

    Parameters
    ----------
    vstruct: dict
    filter_by: str
        site key to filter by
    allowed: list
        list of allowed values
    deepcopy:
        deepcopy structure before altering

    Returns
    -------

    """
    vstruct = process_vstruct(vstruct, ["repeat_cell"], deepcopy=deepcopy)
    for element in vstruct["elements"]:
        element["sites"] = [s for s in element["sites"] if s[filter_by] in allowed]
    return vstruct


def color_by_func(vstruct, sitekey, colmap, fill_color=True, outline_color=False, deepcopy=False):
    """

    Parameters
    ----------
    vstruct: dict
    sitekey: str
    colmap: func
    fill_color: bool
        whether to change atom fill color
    outline_color: bool
        whether to change atom outline color
    deepcopy:
        deepcopy structure before altering

    Returns
    -------

    """
    vstruct = process_vstruct(vstruct, ["repeat_cell"], deepcopy=deepcopy)
    for element in vstruct["elements"]:
        for site in element["sites"]:
            if fill_color:
                site["color_fill"] = colmap(site[sitekey])
            if outline_color:
                site["color_outline"] = colmap(site[sitekey])
    return vstruct


def color_by_mpl(vstruct, sitekey, cmap_name="jet", vrange=(0., 1.), fill_color=True, outline_color=False, deepcopy=False):
    """

    Parameters
    ----------
    vstruct: dict
    sitekey: str
    cmap_name: str
    vrange: tuple
    fill_color: bool
        whether to change atom fill color
    outline_color: bool
        whether to change atom outline color
    deepcopy:
        deepcopy structure before altering

    Returns
    -------

    """
    norm = Normalize(vmin=vrange[0], vmax=vrange[1])
    cmap = get_cmap(cmap_name)

    def cmap_func(x):
        r, g, b, a = cmap(norm(x))
        return r, g, b

    return color_by_func(vstruct, sitekey, cmap_func, fill_color, outline_color, deepcopy)


def _repeat_repeat_cell(vstruct, repeats=(0, 0, 0), recentre=True):
    for indx, cvector, rep in zip([0, 1, 2], ["a", "b", "c"], repeats):

        if not isinstance(rep, int):
            raise ValueError("repetition must be an integer value")
        if rep == 0:
            continue

        # init_coords = vstruct['coords'][:]
        repv = np.asarray(vstruct['cell_vectors'][cvector], dtype=float)
        newvector = repv * (abs(rep) + 1)
        vstruct['cell_vectors'][cvector] = newvector.tolist()

        init_sites = vstruct["sites"][:]
        for r in range(abs(rep)):
            v = -repv * (r + 1) if rep < 0 else repv * (r + 1)
            new_coords = []
            for site in init_sites:
                new_site = copy.deepcopy(site)
                new_site["ccoord"] = (np.array(site["ccoord"], dtype=float) + v).tolist()
                new_site["cell"][indx] += r + 1
                vstruct["sites"].append(new_site)

        if recentre:
            centre = np.asarray(vstruct['centre'])
            centre = centre + repv * (abs(rep)) / 2.
            vstruct['centre'] = centre.tolist()


def _translate_to_repeat_cell(vstruct, centre=(0., 0., 0.)):
    centre = np.asarray(centre, dtype=float)
    tr = centre - np.asarray(vstruct['centre'], dtype=float)
    vstruct['centre'] = centre.tolist()
    for site in vstruct["sites"]:
        site["ccoord"] = (np.array(site["ccoord"], dtype=float) + tr).tolist()


# TODO not centred at origin, normal rotate
# def _align_repeat_cell(vstruct, cvector='a', direction=(1, 0, 0)):
#     """align cell vector to a cartesian direction"""
#     direction = np.asarray(direction, dtype=float)
#     v = vstruct['cell_vectors'][cvector]
#
#     coords = np.array([s["ccoord"] for s in vstruct['sites']])
#     new_coords = realign_vectors(coords, v, direction)
#     for site, new in zip(vstruct['sites'], new_coords):
#         site["ccoord"] = new.tolist()
#
#     new_cell = realign_vectors([vstruct['cell_vectors']['a'],
#                                 vstruct['cell_vectors']['b'],
#                                 vstruct['cell_vectors']['c'],
#                                 vstruct['centre']], v, direction)
#     vstruct['cell_vectors']['a'] = new_cell[0].tolist()
#     vstruct['cell_vectors']['b'] = new_cell[1].tolist()
#     vstruct['cell_vectors']['c'] = new_cell[2].tolist()
#     vstruct['centre'] = new_cell[3].tolist()


def _cslice_repeat_cell(vstruct, normal=(1, 0, 0), lbound=None, ubound=None, centre=None):
    normal = np.asarray(normal, dtype=float)
    centre = vstruct['centre'] if centre is None else centre
    coords = np.array([s["ccoord"] for s in vstruct['sites']])
    mask = slice_mask(coords, normal, lbound, ubound, centre)
    vstruct['sites'] = [s for m, s in zip(mask, vstruct['sites']) if m]
