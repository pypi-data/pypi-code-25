import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from jsonextended import edict
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.cm import get_cmap
from matplotlib.colorbar import ColorbarBase
from matplotlib.patches import Circle as MplCircle
from matplotlib.colors import to_rgb, Normalize, LinearSegmentedColormap
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ipyatom.transforms import apply_transforms
from ipyatom.repeat_density import cube_frac2cart, cubesliceplane, sliceplane_points
from ipyatom.utils import fmt_scientific


def _color_to_rgb(item):
    try:
        if item.startswith('rgb('):
            item = item[4:-1].split(',')
            item = tuple([float(v) / 255 for v in item])
    except AttributeError:
        pass
    return to_rgb(item)


def _lighter_color(color, fraction=0.1):
    """returns a lighter color

    color: (r,g,b)
    fraction: [0,1] to lighten by
    """
    if fraction == 0.:
        return color
    assert 0 < fraction <= 1, 'fraction must be between 0 and 1'
    white = np.array([1., 1., 1.])
    vector = white - color
    return color + vector * fraction


def create_colorbar(cax, cmap_range=(0, 1), cmap_name="jet",
                    colorbar_title="", colorbar_loc="top", ticksize=8):
    """ create colorbar

    see https://matplotlib.org/devdocs/tutorials/colors/colorbar_only.html

    Parameters
    ----------
    cax: matplotlib.axes.Axes
    cmap_name: str
    cmap_range: tuple
    colorbar_title: str
    colorbar_loc: str
        'top' or 'bottom'
    ticksize: int

    """
    assert colorbar_loc == "top" or colorbar_loc == "bottom"
    norm = Normalize(vmin=cmap_range[0], vmax=cmap_range[1])
    cmap = get_cmap(cmap_name)
    cbar = ColorbarBase(cax, cmap=cmap, norm=norm, orientation="horizontal",
                        label=colorbar_title, ticklocation=colorbar_loc, extend="both")
    cax.tick_params(labelsize=ticksize)
    return cbar


def plot_atoms_top(vstruct, apply_depth=True, color_depth=None, axis_range=None, linewidth=None,
                   ax=None, legend=None, show_legend=True, legend_title=None,
                   show_colorbar=False, cmap_name="jet", cmap_range=(0., 1.), colorbar_title="",
                   colorbar_loc="top"):
    """plot atoms and bounding boxes as top-down orthographic image,
    with atoms color lightened with decreasing z coordinate

    Parameters
    ----------
    vstruct : dict
    apply_depth: bool
        lighten color by z-depth
    color_depth: float
        z-depth at which colors are completely lightened
    axis_range : tuple
        (xmin,xmax,ymin,ymax)
    linewidth: float or None
    ax: matplotlib.axes.Axes
    show_legend: bool
    legend: dict
        items to append to legend, e.g. {name: matplotlib.lines.Line2D, ...}
    legend_title: str
    show_colorbar: bool
    cmap_name: str
    cmap_range: tuple
    colorbar_title: str
    colorbar_loc: str
        'top' or 'bottom'

    """
    assert colorbar_loc == "top" or colorbar_loc == "bottom"
    new_struct = apply_transforms(vstruct)

    new_ax = False
    if ax is None:
        fig = plt.figure()
        # initialize axis, important: set the aspect ratio to equal
        ax = fig.add_subplot(111, aspect='equal')
        new_ax = True
    legend = {} if legend is None else legend

    scatters = edict.filter_keyvals(new_struct, {"type": "repeat_cell"}, list_of_dicts=True, keep_siblings=True)
    scatters = [edict.combine_lists(s, ["sites"], deepcopy=False) for s in scatters["elements"]]
    scatters = edict.remove_keys({"s": scatters}, ["sites"], list_of_dicts=True, deepcopy=False)["s"]

    # create list of atoms
    flatten = lambda l: [item for sublist in l for item in sublist]
    # items = [len(v['ccoords']) for v in scatters]
    coords = flatten([v['ccoord'] for v in scatters])
    df = pd.DataFrame({
        'x': [v[0] for v in coords],
        'y': [v[1] for v in coords],
        'z': [v[2] for v in coords],
        # 'visible': flatten([[v['visible']] * i for i, v in zip(items, scatters)]),
        'radius': flatten([v['radius'] for v in scatters]),
        'transparency': flatten([v['transparency'] for v in scatters]),
        'color': flatten([v['color_fill'] for v in scatters]),
        'edgecolor': flatten([v['color_outline'] for v in scatters]),
    })
    # df = df[df.visible]
    df.color = df.color.apply(_color_to_rgb)

    if color_depth is not None:
        clip = (df.z.max() - color_depth, df.z.max())
    else:
        clip = (df.z.min(), df.z.max())

    if new_ax:
        default_axis_range = [(df.x - df.radius).min(), (df.x + df.radius).max(),
                              (df.y - df.radius).min(), (df.y + df.radius).max()]
    else:
        xmin, xmax = ax.get_xbound()
        ymin, ymax = ax.get_ybound()
        default_axis_range = [min(xmin, (df.x - df.radius).min()), max(xmax, (df.x + df.radius).max()),
                              min(ymin, (df.y - df.radius).min()), max(ymax, (df.y + df.radius).max())]

    sort_mask = df.z.argsort()
    z_clipped = np.clip(df.z, clip[0], clip[1])
    if z_clipped.max() == z_clipped.min():
        z_norm = np.ones_like(z_clipped)
    else:
        z_norm = (z_clipped - clip[0]) / (clip[1] - clip[0])

    lbound, ubound = 0.1, 1.
    z_scaled = (z_norm * (ubound - lbound)) + lbound

    if apply_depth:
        zcolor = np.array([_lighter_color(c, 1 - f) for c, f in zip(df.color.values, z_scaled)])
    else:
        zcolor = df.color.values

    # create 2d atoms
    for (i, row), zcolor in zip(df.iloc[sort_mask].iterrows(), zcolor[sort_mask]):
        ax.add_artist(MplCircle(xy=(row.x, row.y), radius=row.radius, linewidth=linewidth,
                                alpha=row.transparency, facecolor=zcolor, edgecolor=row.edgecolor))

    if show_legend:
        for scatter in scatters:
            for color, label in set(zip(scatter['color_fill'], scatter['label'])):
                color = _color_to_rgb(color)
                if scatter['name']:
                    label += ' (' + scatter['name'] + ')'

                artist = plt.Line2D((0, 1), (0, 0), color=color, marker='o', linestyle='')
                if label in legend:
                    raise ValueError('attempting to set muliple legend keys for label: {}'.format(label))
                legend[label] = artist

        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # Put a legend to the right of the current axis
        labels = sorted(legend.keys())
        handles = [legend[k] for k in labels]
        ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5), title=legend_title)

    if axis_range is not None:
        xmin, xmax, ymin, ymax = axis_range
        ax.set_xbound(xmin, xmax)
        ax.set_ybound(ymin, ymax)
    else:
        xmin, xmax, ymin, ymax = default_axis_range
        ax.set_xbound(xmin, xmax)
        ax.set_ybound(ymin, ymax)

    if show_colorbar:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(colorbar_loc, size='5%', pad=0.2)
        # see https://matplotlib.org/devdocs/tutorials/colors/colorbar_only.html
        create_colorbar(cax, cmap_range=cmap_range, cmap_name=cmap_name,
                        colorbar_title=colorbar_title, colorbar_loc=colorbar_loc)

    return ax, legend


def plot_slice(vstruct, scentre, snormal, cell_size=None, contourf=True,
               cmap='viridis', cmap_range=(None, None), bval=np.nan, cbar_tick_rot=0,
               show_corners=True, orientation=None, alter_bbox=(0., 0., 0., 0.),
               angle_step=1., dist_tol=1e-5, min_voxels=None, max_voxels=None):
    """

    Parameters
    ----------
    vstruct: dict
    scentre: Tuple
        point on slice plane (x, y, z)
    snormal: Tuple
        norma of slice plane (x, y, z)
    cell_size: float
        length of discretised cells. If None, cell_size = <minimum cube length> * 0.01
    contourf: bool or list of bools
        use filled contour, else lines. If list, set independantly for each element
    cmap: str or list of str
        cmap type.  If list, set independantly for each element
    cmap_range: tuple or list of tuples
        range for colors. If list, set independantly for each element
    bval: float or list of floats
        value to set as background for contour plots. If list, set independantly for each element
    cbar_tick_rot: float
        rotation of colorbar axis tick labels
    show_corners: bool of list of bool
        whether to show real space (x,y,z) plot corner positions. If list, set independantly for each element
    orientation: int or None
        between 0 and 3, select a specific bbox orientation (rotated by orientation * 90 degrees)
        if None, the orientation is selected such that corner min(x',y') -> min(x,y,z)
    alter_bbox: tuple of floats
        move edges of computed bbox (bottom, top, left, right)
    angle_step: float
        angular step (degrees) for mapping plane intersection with bounding box
    dist_tol: float
        distance tolerance for finding edge of bounding box
    min_voxels : int
        minimum number of voxels in cartesian density cube
    max_voxels : int
        maximum number of voxels in cartesian density cube

    Returns
    -------
    fig: matplotlib.figure.Figure
    final_axes: list
        [(ax, cbar_ax), ...] for each element

    """
    # cbar_fmt: matplotlib.ticker.Formatter
    #        formatter for converting colorbar tick labels to str, if None use scientific notation
    new_struct = apply_transforms(vstruct)

    acceptable_elements = [e for e in new_struct["elements"] if e["type"] in ["repeat_cell", "repeat_density"]]
    num_elements = len(acceptable_elements)
    if num_elements == 0:
        raise ValueError("no 'repeat_cell' or 'repeat_density' elements present in vstruct")

    if isinstance(contourf, bool):
        contourf = [contourf for _ in range(num_elements)]
    if not (isinstance(cmap, list) or isinstance(cmap, tuple)):
        cmap = [cmap for _ in range(num_elements)]
    if not (isinstance(bval, list) or isinstance(bval, tuple)):
        bval = [bval for _ in range(num_elements)]
    if not (isinstance(cmap_range, list)):
        cmap_range = [cmap_range for _ in range(num_elements)]
    if isinstance(show_corners, bool):
        show_corners = [show_corners for _ in range(num_elements)]

    # fig = plt.figure()
    # ax = fig.add_subplot(111, aspect='equal')  # type: Axes

    fig, axes = plt.subplots(1, num_elements, subplot_kw={"aspect": "equal"}, sharex='all', sharey='all', squeeze=True)
    fig = fig  # type: Figure
    if num_elements == 1:
        axes = [axes]

    final_axes = []

    for element, ax, el_contourf, el_cmap, el_bval, (el_vmin, el_vmax), el_corners in zip(
            new_struct["elements"], axes, contourf, cmap, bval, cmap_range, show_corners):
        ax = ax  # type: Axes

        if element["type"] == "repeat_density":
            cbar_title = "{0} ({1})".format(element["name"], element["dtype"])

            print("running cube_frac2cart")
            out = cube_frac2cart(element['dcube'], element['cell_vectors']['a'],
                                 element['cell_vectors']['b'], element['cell_vectors']['c'],
                                 element['centre'], max_voxels=max_voxels, min_voxels=min_voxels, make_cubic=False)
            ccube, (xmin, ymin, zmin), (xmax, ymax, zmax) = out
            print("running cubesliceplane")
            corners, corners_xy, gvalues_xy = cubesliceplane(ccube, (xmin, xmax, ymin, ymax, zmin, zmax),
                                                             scentre, snormal, cell_size=cell_size, bval=el_bval,
                                                             orientation=orientation, alter_bbox=alter_bbox,
                                                             angle_step=angle_step, dist_tol=dist_tol)
            x, y, z = gvalues_xy.T
            cmap = get_cmap(el_cmap)
        elif element["type"] == "repeat_cell":
            cbar_title = "{0} ({1})".format(element["name"], "nuclei")
            centre = np.asarray(element['centre'], dtype=float)
            v1 = np.asarray(element['cell_vectors']['a'])
            v2 = np.asarray(element['cell_vectors']['b'])
            v3 = np.asarray(element['cell_vectors']['c'])
            bbox_pts = np.asarray([np.array([0.0, 0.0, 0.0]), v1, v2, v3, v1 + v2, v1 + v3, v1 + v2 + v3, v2 + v3])
            bbox_x, bbox_y, bbox_z = bbox_pts.T
            xmin, xmax, ymin, ymax, zmin, zmax = (bbox_x.min(), bbox_x.max(), bbox_y.min(),
                                                  bbox_y.max(), bbox_z.min(), bbox_z.max())  # l,r,bottom,top
            xmin, ymin, ymin = np.array((xmin, ymin, ymin)) - 0.5 * (v1 + v2 + v3) + np.array(centre)
            xmax, ymax, zmax = np.array((xmax, ymax, zmax)) - 0.5 * (v1 + v2 + v3) + np.array(centre)
            corners, corners_xy, gpoints, gpoints_xy = sliceplane_points((xmin, xmax, ymin, ymax, zmin, zmax),
                                                                         scentre, snormal, cell_size,
                                                                         orientation, alter_bbox, angle_step, dist_tol)

            gvalues = np.full((gpoints_xy.shape[0],), 0, dtype=np.float64)
            # create a map of site labels to color and index
            color_map = {(d[0], d[1]): i + 1 for i, d in enumerate(sorted(
                set([(site["label"], site["color_fill"]) for site in element["sites"]])))}
            for site in element["sites"]:
                mask = np.abs(np.linalg.norm(gpoints - site["ccoord"], axis=1)) < site["radius"]
                gvalues[mask] = color_map[(site["label"], site["color_fill"])]
            x, y = gpoints_xy.T
            z = gvalues

            # make cmap be correct for color_map
            v2colmap = {v: k[1] for k, v in color_map.items()}
            clist = ["white"] + [v2colmap[k] for k in sorted(v2colmap.keys())]
            cmap = LinearSegmentedColormap.from_list("cmap_name", clist, N=len(clist))
        else:
            continue

        el_vmin = np.nanmin(z) if el_vmin is None else el_vmin
        el_vmax = np.nanmax(z) if el_vmax is None else el_vmax

        cbar_fmt = ticker.FuncFormatter(fmt_scientific)
        min_exp, min_diff_exp = (2, 2)
        exp_min, exp_max = int('{:.2e}'.format(el_vmin).split('e')[1]), int('{:.2e}'.format(el_vmax).split('e')[1])
        if abs(exp_min - exp_max) < min_diff_exp and abs(exp_min) > min_exp:
            el_multiplier = 10 ** float(exp_min)
            el_vmin /= el_multiplier
            el_vmax /= el_multiplier
            z /= el_multiplier
            cbar_title += r" $\times 10^{{{}}}$".format(int(exp_min))

        x_axis, x_arr = np.unique(x, return_inverse=True)
        y_axis, y_arr = np.unique(y, return_inverse=True)
        z_array = np.full((np.max(y_arr) + 1, np.max(x_arr) + 1), np.nan)
        z_array[y_arr, x_arr] = z

        print("plotting contour")
        if el_contourf:
            cset = ax.contourf(x_axis, y_axis, z_array, cmap=cmap,
                               vmin=el_vmin, vmax=el_vmax, extend='both')
        else:
            cset = ax.contour(x_axis, y_axis, z_array, cmap=cmap,
                              vmin=el_vmin, vmax=el_vmax, extend='both')

        norm = Normalize(vmin=el_vmin, vmax=el_vmax)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('bottom', size='5%', pad=0.3)
        # see https://matplotlib.org/devdocs/tutorials/colors/colorbar_only.html
        cbar = ColorbarBase(cax, cmap=cmap, norm=norm, orientation="horizontal",
                            ticklocation="bottom", extend="both", format=cbar_fmt)
        cbar.set_label(cbar_title, fontsize=8)

        if element["type"] == "repeat_cell":
            v2labelmap = {v: k[0] for k, v in color_map.items()}
            cbar.set_ticks(sorted(v2labelmap.keys()))
            cbar.set_ticklabels([v2labelmap[k] for k in sorted(v2labelmap.keys())])

        cax.tick_params(labelsize=8)
        for tick in cax.get_xticklabels():
            tick.set_rotation(cbar_tick_rot)

        if el_corners:
            crnrs = [c for c in zip(corners_xy, corners)]
            for cxy, c3d in [crnrs[2], crnrs[0], crnrs[3], crnrs[1]]:
                ax.scatter([cxy[0]], [cxy[1]], label="({0:.2f}, {1:.2f}, {2:.2f})".format(*c3d), edgecolor='black')
            # ax.legend(ncol=1, loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize="x-small",
            #           title="Coordinate\nMapping")
            ax.legend(ncol=2, loc='lower center', fontsize="x-small", bbox_to_anchor=(0.5, 1.0),
                      title="Coordinate Mapping", framealpha=0.5)

        final_axes.append((ax, cax))

    return fig, final_axes


if __name__ == "__main__":

    if False:
        from ase.build import bulk
        from ipyatom.repeat_cell import atoms_to_dict, color_by_mpl

        fe = bulk("Fe").repeat((5, 5, 5))

        dct = atoms_to_dict(fe, name="BCC", charge=np.random.rand(fe.get_number_of_atoms()))
        dct = color_by_mpl(dct, "charge", vrange=(0, 1), outline_color=True, fill_color=False)
        plot_atoms_top(dct, linewidth=5, show_colorbar=True, colorbar_title="Charge", cmap_range=(0, 1))
        plt.show()

    if True:
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
                         "color_fill": "green",
                         "color_outline": None
                     },
                     {
                         "radius": .5,
                         "transparency": 1,
                         "label": "S",
                         "ccoord": [.5, 0, .5],
                         "color_fill": "blue",
                         "color_outline": None
                     },
                     {
                         "radius": .2,
                         "transparency": 1,
                         "label": "H",
                         "ccoord": [.5, 1.25, .5],
                         "color_fill": "red",
                         "color_outline": None
                     }

                 ]

                 }

            ]
        }

        # an example of a cbar formatter
        # cmap_format = ticker.ScalarFormatter(useMathText=True)
        # cmap_format.set_powerlimits((0, 0))
        # cbar.formatter.set_useOffset(True)
        # cbar.update_ticks()

        fig1, axes1 = plot_slice(instruct, (0.5, 0.5, 0.5), (0., 0., 1.),
                                 cell_size=.001, min_voxels=10000, cmap_range=(None, None),
                                 contourf=[True, True, True], bval=[np.nan, np.nan, 0],
                                 show_corners=[False, True, False], cbar_tick_rot=45)
        fig1.tight_layout(rect=[0, 0.05, .9, .85])
        plt.show()
