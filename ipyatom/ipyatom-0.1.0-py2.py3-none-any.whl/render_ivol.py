from collections import OrderedDict

import numpy as np
from ipyatom.bonds import compute_bonds
from ipyatom.transforms import apply_transforms
from jsonextended import edict
from scipy.spatial.qhull import ConvexHull

from ipyatom.repeat_density import cube_frac2cart

# don't make required just yet
try:
    import ipyvolume.pylab as p3
except ImportError:
    pass
try:
    import ipywidgets as widgets
except ImportError:
    pass


def _create_mesh(points, color="black", solid=False, lines=True, triangle_indices=None, line_indices=None):
    """ create an ipyvolume mesh from a number of points

    Parameters
    ----------
    points: list
        [[x, y, z], ...]
    color: str
    solid: bool
    triangle_indices: list or None
        [[i, j, k], ...], if None then computed from scipy.spatial.qhull.ConvexHull triangles
    line_indices: list or None
        [[i, j], ...], if None then computed from scipy.spatial.qhull.ConvexHull triangles

    Returns
    -------

    """
    x, y, z = np.array(points).T
    try:
        hull = ConvexHull(points)
    except:
        hull = ConvexHull(points, qhull_options='QJ')
    if triangle_indices is None:
        triangle_indices = hull.simplices.tolist()
    if line_indices is None:
        line_indices = []
        for i, j, k in hull.simplices.tolist():
            line_indices += [[i, j], [i, k], [j, k]]

    mesh = p3.plot_trisurf(x, y, z, triangles=triangle_indices, lines=line_indices, color=color)
    if not solid:
        mesh.visible_faces = False
    if not lines:
        mesh.visible_lines = False
    return mesh


def _get_cylinder_mesh(p0, p1, radius=1, segments=50):
    """

    Parameters
    ----------
    p0: list or numpy.array((3,))
    p1: list or numpy.array((3,))
    radius: float
    segments: int

    Returns
    -------

    """
    p0 = np.array(p0)
    p1 = np.array(p1)
    # vector in direction of axis
    v = p1 - p0
    # find magnitude of vector
    mag = np.linalg.norm(v)
    # unit vector in direction of axis
    v = v / mag
    # make some vector not in the same direction as v
    not_v = np.array([1, 0, 0])
    if (v == not_v).all() or (v == -not_v).all():
        not_v = np.array([0, 1, 0])
    # make vector perpendicular to v
    n1 = np.cross(v, not_v)
    # normalize n1
    n1 /= np.linalg.norm(n1)
    # make unit vector perpendicular to v and n1
    n2 = np.cross(v, n1)
    # surface ranges over t from 0 to length of axis and 0 to 2*pi
    t = np.linspace(0, mag, 2)
    theta = np.linspace(0, 2 * np.pi, segments)
    # use meshgrid to make 2d arrays
    t, theta = np.meshgrid(t, theta)
    # generate coordinates for surface
    X, Y, Z = [p0[i] + v[i] * t + radius * np.sin(theta) * n1[i] + radius * np.cos(theta) * n2[i] for i in [0, 1, 2]]
    return list(zip(X[:, 0], Y[:, 0], Z[:, 0])) + list(zip(X[:, 1], Y[:, 1], Z[:, 1]))


def _create_bond(p1, p2, c1, c2=None, radius=.1, segments=20):
    """ create a bond

    Parameters
    ----------
    p1: list or numpy.array((3,))
    p2: list or numpy.array((3,))
    c1: str or numpy.array((3,))
    c2: str or numpy.array((3,))
    radius: float
    segments: int

    """
    if c2 is None or np.all(c1 == c2):
        return [_create_mesh(_get_cylinder_mesh(p1, p2, radius=radius, segments=segments),
                             c1, solid=True, lines=False)]
    else:
        p1 = np.array(p1)
        p2 = np.array(p2)
        pmid = p1 + 0.5 * (p2 - p1)
        m1 = _create_mesh(_get_cylinder_mesh(p1, pmid, radius=radius, segments=segments),
                          c1, solid=True, lines=False)
        m2 = _create_mesh(_get_cylinder_mesh(pmid, p2, radius=radius, segments=segments),
                          c2, solid=True, lines=False)
        return [m1, m2]


def create_ivol(vstruct,
                width=500, height=400, ssize=5,
                min_voxels=None,  max_voxels=None, **volargs):
    """

    Parameters
    ----------
    vstruct: dict
    width: int
    height: int
    ssize: int
    min_voxels : int
        minimum number of voxels in density cube
    max_voxels : int
        maximum number of voxels in density cube
    volargs: dict

    Returns
    -------

    Examples
    --------

    >>> from jsonextended import edict

    >>> dstruct = {
    ...  'type': 'repeat_density',
    ...  'dtype': 'charge',
    ...  'name': '',
    ...  'dcube':np.ones((3,3,3)),
    ...  'centre':[0,0,0],
    ...  'cell_vectors':{
    ...      'a':[2.,0,0],
    ...      'b':[0,2.,0],
    ...      'c':[0,0,2.]},
    ...   'color_bbox': 'black',
    ...   'transforms': []
    ... }
    >>> cstruct = {
    ...  'type': 'repeat_cell',
    ...  'name': '',
    ...  'centre':[0,0,0],
    ...  'cell_vectors':{
    ...      'a':[2.,0,0],
    ...      'b':[0,2.,0],
    ...      'c':[0,0,2.]},
    ...   'color_bbox': 'black',
    ...   'sites': [{
    ...         'label': "Fe",
    ...         'ccoord': [1,1,1],
    ...         'color_fill': "red",
    ...         'color_outline': None,
    ...         'transparency': 1,
    ...         'radius': 1,
    ...   }],
    ...   'bonds': [],
    ...   'transforms': []
    ... }
    >>> vstruct = {"elements": [dstruct, cstruct], "transforms": []}
    >>> new_struct, fig, controls = create_ivol(vstruct)

    >>> print(edict.apply(edict.filter_keys(new_struct, ["ivol"], list_of_dicts=True),
    ...                   "ivol", lambda x: [v.__class__.__name__ for v in x], list_of_dicts=True))
    {'elements': [{'ivol': ['Figure', 'Mesh']}, {'ivol': ['Mesh', 'Scatter']}]}

    """
    new_struct = apply_transforms(vstruct)
    bonds = compute_bonds(new_struct)#edict.filter_keyvals(vstruct, {"type": "repeat_cell"}, keep_siblings=True))

    # ivolume currently only allows one volume rendering per plot
    # voltypes = edict.filter_keyvals(vstructs,[('type','repeat_density')])
    vol_index = [i for i, el in enumerate(vstruct['elements'])
                 if el['type'] == 'repeat_density']
    assert len(vol_index) <= 1, "ipyvolume only allows one volume rendering per scene"

    p3.clear()
    fig = p3.figure(width=width, height=height, controls=True)
    fig.screen_capture_enabled = True

    # the volume rendering must be created first,
    # for appropriately scaled axis
    if vol_index:
        volstruct = new_struct['elements'][vol_index[0]]
        a = volstruct['cell_vectors']['a']
        b = volstruct['cell_vectors']['b']
        c = volstruct['cell_vectors']['c']
        centre = volstruct['centre']
        #print(centre)


        # convert dcube to cartesian
        out = cube_frac2cart(volstruct['dcube'], a, b, c, centre,
                             max_voxels=max_voxels, min_voxels=min_voxels, make_cubic=True)
        new_density, (xmin, ymin, zmin), (xmax, ymax, zmax) = out

        vol = p3.volshow(new_density, **volargs)

        if volstruct["color_bbox"] is not None:
            a = np.asarray(a)
            b = np.asarray(b)
            c = np.asarray(c)
            o = np.asarray(centre) - 0.5*(a+b+c)
            mesh = _create_mesh([o, o+a, o+b, o+c, o+a+b, o+a+c, o+c+b, o+a+b+c], color=volstruct["color_bbox"],
                                line_indices=[[0, 1], [0, 2], [0, 3], [2, 4], [2, 6],
                                              [1, 4], [1, 5], [3, 5], [3, 6], [7, 6], [7, 4], [7, 5]])
            vol = [vol, mesh]

        # todo better way of storing ivol components?
        volstruct['ivol'] = vol

        # appropriately scale axis
        p3.xlim(xmin, xmax)
        p3.ylim(ymin, ymax)
        p3.zlim(zmin, zmax)

    for element in new_struct['elements']:
        if element['type'] == 'repeat_density':
            continue
        elif element['type'] == 'repeat_cell':
            scatters = []
            if element["color_bbox"] is not None:
                a = np.asarray(element['cell_vectors']['a'])
                b = np.asarray(element['cell_vectors']['b'])
                c = np.asarray(element['cell_vectors']['c'])
                centre = element['centre']
                o = np.asarray(centre) - 0.5 * (a + b + c)
                mesh = _create_mesh([o, o + a, o + b, o + c, o + a + b, o + a + c, o + c + b, o + a + b + c],
                                    color=element["color_bbox"],
                                    line_indices=[[0, 1], [0, 2], [0, 3], [2, 4], [2, 6],
                                                  [1, 4], [1, 5], [3, 5], [3, 6], [7, 6], [7, 4], [7, 5]])
                scatters.append(mesh)

            for color, radius in set([(s['color_fill'], s['radius']) for s in element["sites"]]):

                scatter = edict.filter_keyvals(element, {"color_fill": color, "radius": radius}, "AND",
                                               keep_siblings=True, list_of_dicts=True)
                scatter = edict.combine_lists(scatter, ["sites"], deepcopy=False)
                scatter = edict.remove_keys(scatter, ["sites"], deepcopy=False)

                x, y, z = np.array(scatter['ccoord']).T
                s = p3.scatter(x, y, z, marker='sphere', size=ssize * radius, color=color)
                scatters.append(s)

            element['ivol'] = scatters
        elif element['type'] == 'repeat_poly':
            polys = []
            for poly in element['polys']:
                mesh = _create_mesh(poly, element['color'], element['solid'])
                polys.append(mesh)
            element['ivol'] = polys
        else:
            raise ValueError("unknown element type: {}".format(element['type']))

    for bond in bonds:
        p1, p2, c1, c2, radius = bond
        meshes = _create_bond(p1, p2, c1, c2, radius)

    # split up controls
    if vol_index:
        (level_ctrls, figbox,
         extractrl1, extractrl2) = p3.gcc().children
        controls = OrderedDict([('transfer function', [level_ctrls]),
                                ('lighting', [extractrl1, extractrl2])])
    else:
        # figbox = p3.gcc().children
        controls = {}

    return new_struct, fig, controls


# def create_ivol_control(vstruct, vparam, ctype, cparam='value', **ckwargs):
#     """
#
#     Parameters
#     ----------
#     vstruct
#     vparam
#     ctype
#     cparam
#     ckwargs
#
#     Returns
#     -------
#
#     """
#     assert 'ivol' in vstruct
#     ctrl = getattr(widgets, ctype)(**ckwargs)
#     widgets.jslink((vstruct['ivol'], vparam), (ctrl, cparam))
#
#     return ctrl


def add_controls(fig, ctrl_layout,
                 top=False):
    """

    Parameters
    ----------
    fig
    ctrl_layout
    top

    Returns
    -------

    """
    if not ctrl_layout:
        return fig
    if isinstance(ctrl_layout, list):
        layout = []
        for cntrl in ctrl_layout:
            if isinstance(cntrl, list):
                cntrl = widgets.HBox(cntrl)
            layout.append(cntrl)
        options = widgets.VBox(layout)
    else:
        tabs = OrderedDict()
        for name, cntrls in ctrl_layout.items():
            layout = []
            for cntrl in cntrls:
                if isinstance(cntrl, list):
                    cntrl = widgets.HBox(cntrl)
                layout.append(cntrl)
            tabs[name] = widgets.VBox(layout)
        options = widgets.Tab(children=tuple(tabs.values()))
        for i, name in enumerate(tabs):
            options.set_title(i, name)

    if top:
        return widgets.VBox([options, fig])
    else:
        return widgets.VBox([fig, options])
