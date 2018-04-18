# -*- coding: utf-8 -*-
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from __future__ import division

from functools import partial
from itertools import izip, product
from warnings import warn

import mne
from nibabel.freesurfer import read_annot
import numpy as np

from .._data_obj import asndvar, NDVar, SourceSpace, UTS
from .._utils import deprecated
from ..fmtxt import Image, im_table, ms
from ._base import EelFigure, ImLayout, ColorBarMixin
from ._color_luts import p_lut, dspm_lut
from ._colors import ColorList


def assert_can_save_movies():
    from ._brain_object import assert_can_save_movies
    assert_can_save_movies()


def annot(annot, subject='fsaverage', surf='smoothwm', borders=False, alpha=0.7,
          hemi=None, views=('lat', 'med'), w=None, h=None, axw=None, axh=None,
          foreground=None, background=None, parallel=True, cortex='classic',
          title=None, subjects_dir=None, name=None):
    """Plot the parcellation in an annotation file

    Parameters
    ----------
    annot : str
        Name of the annotation (e.g., "PALS_B12_LOBES").
    subject : str
        Name of the subject (default 'fsaverage').
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    borders : bool | int
        Show only label borders (PySurfer Brain.add_annotation() argument).
    alpha : scalar
        Alpha of the annotation (1=opaque, 0=transparent, default 0.7).
    hemi : 'lh' | 'rh' | 'both' | 'split'
        Which hemispheres to plot (default includes hemisphere with more than one
        label in the annot file).
    views : str | iterator of str
        View or views to show in the figure. Options are: 'rostral', 'parietal',
        'frontal', 'ventral', 'lateral', 'caudal', 'medial', 'dorsal'.
    w, h, axw, axh : scalar
        Layout parameters (figure width/height, subplot width/height).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    title : str
        title for the window (default is the parcellation name).
    subjects_dir : None | str
        Override the default subjects_dir.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 

    Returns
    -------
    brain : surfer.Brain
        PySurfer Brain instance.

    Notes
    -----
    The ``Brain`` object that is returned has a
    :meth:`~plot._brain_fixes.plot_legend` method to plot the color legend.

    See Also
    --------
    eelbrain.plot.brain.annot_legend : plot a corresponding legend without the brain
    """
    if hemi is None:
        annot_lh = mne.read_labels_from_annot(subject, annot, 'lh',
                                              subjects_dir=subjects_dir)
        use_lh = len(annot_lh) > 1
        annot_rh = mne.read_labels_from_annot(subject, annot, 'rh',
                                              subjects_dir=subjects_dir)
        use_rh = len(annot_rh) > 1
        if use_lh and use_rh:
            hemi = 'split'
        elif use_lh:
            hemi = 'lh'
        elif use_rh:
            hemi = 'rh'
        else:
            raise ValueError("Neither hemisphere contains more than one label")

    if title is None:
        title = '%s - %s' % (subject, annot)

    from ._brain_object import Brain
    brain = Brain(subject, hemi, surf, title, cortex,
                  views=views, w=w, h=h, axw=axw, axh=axh,
                  foreground=foreground, background=background,
                  subjects_dir=subjects_dir, name=name)

    brain._set_annot(annot, borders, alpha)
    if parallel:
        brain.set_parallel_view(scale=True)
    return brain


def annot_legend(lh, rh, *args, **kwargs):
    """Plot a legend for a freesurfer parcellation

    Parameters
    ----------
    lh : str
        Path to the lh annot-file.
    rh : str
        Path to the rh annot-file.
    labels : dict (optional)
        Alternative (text) label for (brain) labels.
    h : 'auto' | scalar
        Height of the figure in inches. If 'auto' (default), the height is
        automatically increased to fit all labels.

    Returns
    -------
    legend : :class:`~eelbrain.plot.ColorList`
        Figure with legend for the parcellation.

    Notes
    -----
    Instead of :func:`~eelbrain.plot.brain.annot_legend` it is usually
    easier to use::

    >>> brain = plot.brain.annoot(annot, ...)
    >>> legend = brain.plot_legend()

    See Also
    --------
    eelbrain.plot.brain.annot : plot the parcellation on a brain model
    """
    _, lh_colors, lh_names = read_annot(lh)
    _, rh_colors, rh_names = read_annot(rh)
    lh_colors = dict(izip(lh_names, lh_colors[:, :4] / 255.))
    rh_colors = dict(izip(rh_names, rh_colors[:, :4] / 255.))
    names = set(lh_names)
    names.update(rh_names)
    colors = {}
    seq = []  # sequential order in legend
    seq_lh = []
    seq_rh = []
    for name in names:
        if name in lh_colors and name in rh_colors:
            if np.array_equal(lh_colors[name], rh_colors[name]):
                colors[name] = lh_colors[name]
                seq.append(name)
            else:
                colors[name + '-lh'] = lh_colors[name]
                colors[name + '-rh'] = rh_colors[name]
                seq_lh.append(name + '-lh')
                seq_rh.append(name + '-rh')
        elif name in lh_colors:
            colors[name + '-lh'] = lh_colors[name]
            seq_lh.append(name + '-lh')
        else:
            colors[name + '-rh'] = rh_colors[name]
            seq_rh.append(name + '-rh')
    return ColorList(colors, seq + seq_lh + seq_rh, *args, **kwargs)


def _plot(data, *args, **kwargs):
    "Plot depending on source space kind"
    if data.source.kind == 'vol':
        return _voxel_brain(data, *args, **kwargs)
    else:
        return brain(data, *args, **kwargs)


def dspm(src, fmin=13, fmax=22, fmid=None, *args, **kwargs):
    """
    Plot a source estimate with coloring for dSPM values (bipolar).

    Parameters
    ----------
    src : NDVar, dims = ([case,] source, [time])
        NDVar with SourceSpace dimension. If stc contains a case dimension,
        the average across cases is taken.
    fmin, fmax : scalar >= 0
        Start- and end-point for the color gradient for positive values. The
        gradient for negative values goes from -fmin to -fmax. Values between
        -fmin and fmin are transparent.
    fmid : None | scalar
        Midpoint for the color gradient. If fmid is None (default) it is set
        half way between fmin and fmax.
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : str | iterator of str
        View or views to show in the figure. Options are: 'rostral', 'parietal',
        'frontal', 'ventral', 'lateral', 'caudal', 'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both' | 'split'
        Which hemispheres to plot (default based on data).
    colorbar : bool
        Add a colorbar to the figure (use ``.plot_colorbar()`` to plot a
        colorbar separately).
    time_label : str
        Label to show time point. Use ``'ms'`` or ``'s'`` to display time in
        milliseconds or in seconds, or supply a custom format string to format
        time values (in seconds; default is ``'ms'``).
    w, h, axw, axh : scalar
        Layout parameters (figure width/height, subplot width/height).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    title : str
        title for the window (default is the subject name).
    smoothing_steps : None | int
        Number of smoothing steps if data is spatially undersampled (pysurfer
        ``Brain.add_data()`` argument).
    mask : bool | matplotlib color
        Shade areas that are not in ``src``. Can be matplotlib color, including
        alpha (e.g., ``(1, 1, 1, 0.5)`` for semi-transparent white).
    subjects_dir : None | str
        Override the subjects_dir associated with the source space dimension.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 

    Returns
    -------
    brain : surfer.Brain
        PySurfer Brain instance containing the plot.
    """
    if fmid is None:
        fmid = (fmax + fmin) / 2
    lut = dspm_lut(fmin, fmid, fmax)
    return _plot(src, lut, -fmax, fmax, *args, **kwargs)


def p_map(p_map, param_map=None, p0=0.05, p1=0.01, p0alpha=0.5, *args,
          **kwargs):
    """Plot a map of p-values in source space.

    Parameters
    ----------
    p_map : NDVar
        Statistic to plot (normally a map of p values).
    param_map : NDVar
        Statistical parameter covering the same data points as p_map. Only the
        sign is used, for incorporating the directionality of the effect into
        the plot.
    p0 : scalar
        Highest p-value that is visible.
    p1 : scalar
        P-value where the colormap changes from ramping alpha to ramping color.
    p0alpha : 1 >= float >= 0
        Alpha at ``p0``. Set to 0 for a smooth transition, or a larger value to
        clearly delineate significant regions (default 0.5).
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : str | iterator of str
        View or views to show in the figure. Options are: 'rostral', 'parietal',
        'frontal', 'ventral', 'lateral', 'caudal', 'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both' | 'split'
        Which hemispheres to plot (default based on data).
    colorbar : bool
        Add a colorbar to the figure (use ``.plot_colorbar()`` to plot a
        colorbar separately).
    time_label : str
        Label to show time point. Use ``'ms'`` or ``'s'`` to display time in
        milliseconds or in seconds, or supply a custom format string to format
        time values (in seconds; default is ``'ms'``).
    w, h, axw, axh : scalar
        Layout parameters (figure width/height, subplot width/height).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    title : str
        title for the window (default is the subject name).
    smoothing_steps : None | int
        Number of smoothing steps if data is spatially undersampled (pysurfer
        ``Brain.add_data()`` argument).
    mask : bool | matplotlib color
        Shade areas that are not in ``p_map``. Can be matplotlib color,
        including alpha (e.g., ``(1, 1, 1, 0.5)`` for semi-transparent white).
    subjects_dir : None | str
        Override the subjects_dir associated with the source space dimension.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 

    Returns
    -------
    brain : surfer.Brain
        PySurfer Brain instance containing the plot.

    Notes
    -----
    In order to make economical use of the color lookup table, p-values are
    remapped for display. P-values larger than ``p0`` are mapped to 0, p-values
    for positive effects to ``[step, p0 + step]`` and p-values
    for negative effects to ``[-step, -(p0 + step)]``.

    Due to this, in order to plot a colorbar only including positive
    differences yse::

    >>> brain.plot_colorbar(clipmin=0)

    and to include only negative effects::

    >>> brain.plot_colorbar(clipmax=0)
    """
    p_map, lut, vmax = p_lut(p_map, param_map, p0, p1, p0alpha)
    return _plot(p_map, lut, -vmax, vmax, *args, **kwargs)


def cluster(cluster, vmax=None, *args, **kwargs):
    """Plot a spatio-temporal cluster

    Plots a cluster with the assumption that all non-zero data should be
    visible, while areas that not part of the cluster are 0.

    Parameters
    ----------
    cluster : NDVar
        The cluster.
    vmax : scalar != 0
        Maximum value in the colormap. Default is the maximum value in the
        cluster.
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : str | iterator of str
        View or views to show in the figure. Options are: 'rostral', 'parietal',
        'frontal', 'ventral', 'lateral', 'caudal', 'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both' | 'split'
        Which hemispheres to plot (default based on data).
    colorbar : bool
        Add a colorbar to the figure (use ``.plot_colorbar()`` to plot a
        colorbar separately).
    time_label : str
        Label to show time point. Use ``'ms'`` or ``'s'`` to display time in
        milliseconds or in seconds, or supply a custom format string to format
        time values (in seconds; default is ``'ms'``).
    w, h, axw, axh : scalar
        Layout parameters (figure width/height, subplot width/height).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    title : str
        title for the window (default is the subject name).
    smoothing_steps : None | int
        Number of smoothing steps if data is spatially undersampled (pysurfer
        ``Brain.add_data()`` argument).
    mask : bool | matplotlib color
        Shade areas that are not in ``cluster``. Can be matplotlib color,
        including alpha (e.g., ``(1, 1, 1, 0.5)`` for semi-transparent white).
    subjects_dir : None | str
        Override the subjects_dir associated with the source space dimension.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 

    Returns
    -------
    brain : surfer.Brain
        PySurfer Brain instance containing the plot.
    """
    if vmax is None:
        vmax = max(cluster.x.max(), -cluster.x.min())
        if vmax == 0:
            raise ValueError("The cluster's data is all zeros")
    elif vmax == 0:
        raise ValueError("vmax can't be 0")
    elif vmax < 0:
        vmax = -vmax

    lut = dspm_lut(0, vmax / 10, vmax)
    return _plot(cluster, lut, -vmax, vmax, *args, **kwargs)


def brain(src, cmap=None, vmin=None, vmax=None, surf='inflated',
          views='lateral', hemi=None, colorbar=False, time_label='ms',
          w=None, h=None, axw=None, axh=None, foreground=None, background=None,
          parallel=True, cortex='classic', title=None, smoothing_steps=None,
          mask=True, subjects_dir=None, colormap=None, name=None, pos=None):
    """Create a PySurfer Brain object with a data layer

    Parameters
    ----------
    src : NDVar ([case,] source, [time]) | SourceSpace
        NDVar with SourceSpace dimension. If stc contains a case dimension,
        the average across cases is taken. If a SourceSpace, the Brain is
        returned without adding any data and corresponding arguments are
        ignored. If ndvar contains integer data, it is plotted as annotation,
        otherwise as data layer.
    cmap : str | array
        Colormap (name of a matplotlib colormap) or LUT array. If ``src`` is an
        integer NDVar, ``cmap`` can be a color dictionary mapping label IDs to
        colors.
    vmin, vmax : scalar
        Endpoints for the colormap. Need to be set explicitly if ``cmap`` is
        a LUT array.
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : str | iterator of str
        View or views to show in the figure. Options are: 'rostral', 'parietal',
        'frontal', 'ventral', 'lateral', 'caudal', 'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both' | 'split'
        Which hemispheres to plot (default based on data).
    colorbar : bool
        Add a colorbar to the figure (use ``.plot_colorbar()`` to plot a
        colorbar separately).
    time_label : str
        Label to show time point. Use ``'ms'`` or ``'s'`` to display time in
        milliseconds or in seconds, or supply a custom format string to format
        time values (in seconds; default is ``'ms'``).
    w, h, axw, axh : scalar
        Layout parameters (figure width/height, subplot width/height).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    title : str
        title for the window (default is the subject name).
    smoothing_steps : None | int
        Number of smoothing steps if data is spatially undersampled (pysurfer
        ``Brain.add_data()`` argument).
    mask : bool | matplotlib color
        Shade areas that are not in ``src``. Can be matplotlib color, including
        alpha (e.g., ``(1, 1, 1, 0.5)`` for semi-transparent white).
    subjects_dir : None | str
        Override the subjects_dir associated with the source space dimension.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 
    pos : tuple of int
        Position of the new window on the screen.

    Returns
    -------
    brain : surfer.Brain
        PySurfer Brain instance containing the plot.
    """
    from ._brain_object import Brain, get_source_dim

    if colormap is not None:
        warn("The colormap parameter is deprecated, use cmap instead",
             DeprecationWarning)
        cmap = colormap

    if isinstance(src, SourceSpace):
        if cmap is not None or vmin is not None or vmax is not None:
            raise TypeError("When plotting SourceSpace, cmap, vmin and vmax "
                            "can not be specified (got %s)" %
                            ', '.join((cmap, vmin, vmax)))
        ndvar = None
        source = src
    else:
        ndvar = asndvar(src)
        if ndvar.has_case:
            ndvar = ndvar.summary()
        source = get_source_dim(ndvar)
        # check that ndvar has the right dimensions
        if ndvar.ndim == 2 and not ndvar.has_dim('time') or ndvar.ndim > 2:
            raise ValueError("NDVar should have dimesions source and "
                             "optionally time, got %r" % (ndvar,))

    if hemi is None:
        if source.lh_n and source.rh_n:
            hemi = 'split'
        elif source.lh_n:
            hemi = 'lh'
        elif not source.rh_n:
            raise ValueError('No data')
        else:
            hemi = 'rh'
    elif (hemi == 'lh' and source.rh_n) or (hemi == 'rh' and source.lh_n):
        if ndvar is None:
            source = source[source._array_index(hemi)]
        else:
            ndvar = ndvar.sub(**{source.name: hemi})
            source = ndvar.get_dim(source.name)

    if subjects_dir is None:
        subjects_dir = source.subjects_dir

    brain = Brain(source.subject, hemi, surf, title, cortex,
                  views=views, w=w, h=h, axw=axw, axh=axh,
                  foreground=foreground, background=background,
                  subjects_dir=subjects_dir, name=name, pos=pos)

    if ndvar is not None:
        if ndvar.x.dtype.kind in 'ui':
            brain.add_ndvar_annotation(ndvar, cmap, False)
        else:
            brain.add_ndvar(ndvar, cmap, vmin, vmax, smoothing_steps, colorbar,
                            time_label)

    if mask is not False:
        if mask is True:
            color = (0, 0, 0)
            alpha = 0.5
        else:
            color = mask
            alpha = None
        brain.add_mask(source, color, smoothing_steps, alpha, subjects_dir)

    if parallel:
        brain.set_parallel_view(scale=True)
    return brain


@deprecated("0.25", brain)
def surfer_brain(*args, **kwargs):
    pass


def _voxel_brain(data, lut, vmin, vmax):
    """Plot spheres for volume source space

    Parameters
    ----------
    data : NDVar
        Data to plot.
    lut : array
        Color LUT.
    vmin, vmax : scalar
        Data range.
    """
    if data.dimnames != ('source',):
        raise ValueError("Can only plot 1 dimensional source space NDVars")

    from mayavi import mlab

    x, y, z = data.source.coordinates.T

    figure = mlab.figure()
    mlab.points3d(x, y, z, scale_factor=0.002, opacity=0.5)
    pts = mlab.points3d(x, y, z, data.x, vmin=vmin, vmax=vmax)
    pts.module_manager.scalar_lut_manager.lut.table = lut
    return figure


################################################################################
# Bin-Tables
############
# Top-level functions for fmtxt image tables and classes for Eelfigures.
# - _x_bin_table_ims() wrap 'x' brain plot function
# - _bin_table_ims() creates ims given a brain plot function

class ImageTable(EelFigure, ColorBarMixin):
    _name = "ImageTable"
    # Initialize in two steps
    #
    #  1) Initialize class to generate layout
    #  2) Use ._res_h and ._res_w to generate images
    #  3) Finalize by calling ._add_ims()
    #

    def __init__(self, n_rows, n_columns, title=None, margins=None, *args, **kwargs):
        layout = ImLayout(n_rows * n_columns, 4/3, 2, margins, {'bottom': 0.5},
                          title, *args, nrow=n_rows, ncol=n_columns,
                          autoscale=True, **kwargs)
        EelFigure.__init__(self, None, layout)

        self._n_rows = n_rows
        self._n_columns = n_columns
        self._res_w = int(round(layout.axw * layout.dpi))
        self._res_h = int(round(layout.axh * layout.dpi))

    def _add_ims(self, ims, column_header, cmap_params, cmap_data):
        for row, column in product(xrange(self._n_rows), xrange(self._n_columns)):
            ax = self._axes[row * self._n_columns + column]
            ax.imshow(ims[row][column])

        # column header (time labels)
        if column_header:
            y = 0.25 / self._layout.h
            for i, label in enumerate(column_header):
                x = (0.5 + i) / self._layout.ncol
                self.figure.text(x, y, label, va='center', ha='center')

        ColorBarMixin.__init__(self, lambda: cmap_params, cmap_data)
        self._show()

    def _fill_toolbar(self, tb):
        ColorBarMixin._fill_toolbar(self, tb)

    def add_row_titles(self, titles, x=0.1, y=0, **kwargs):
        """Add a title for each row of images

        Parameters
        ----------
        titles : sequence of str
            Titles, from top to bottom.
        x : scalar
            Horizontal distance from left of the figure.
        y : scalar
            Vertical distance from the top of the axes.
        ...
            Matplotlib text parameters.
        """
        if len(titles) > self._n_rows:
            raise ValueError("%i titles for %i rows: titles=%r" %
                             (len(titles), self._n_rows))
        y_top = self._layout.margins['top'] - y
        y_offset = self._layout.margins['hspace'] + self._layout.axh
        x_ = x / self._layout.w
        for i, label in enumerate(titles):
            y_ = 1 - (y_top + i * y_offset) / self._layout.h
            self.figure.text(x_, y_, label, **kwargs)
        self.draw()


class _BinTable(EelFigure, ColorBarMixin):
    """Super-class"""
    _name = "BinTable"

    def __init__(self, ndvar, tstart, tstop, tstep, im_func, surf, views, hemi,
                 summary, title, foreground=None, background=None,
                 parallel=True, smoothing_steps=None, mask=True, margins=None,
                 *args, **kwargs):
        if isinstance(views, str):
            views = (views,)
        data = ndvar.bin(tstep, tstart, tstop, summary)
        n_columns = len(data.time)
        n_hemis = (data.source.lh_n > 0) + (data.source.rh_n > 0)
        n_rows = len(views) * n_hemis

        layout = ImLayout(n_rows * n_columns, 4/3, 2, margins, {'bottom': 0.5},
                          title, *args, nrow=n_rows, ncol=n_columns, **kwargs)
        EelFigure.__init__(self, None, layout)

        res_w = int(layout.axw * layout.dpi)
        res_h = int(layout.axh * layout.dpi)
        ims, header, cmap_params = im_func(data, surf, views, hemi, axw=res_w,
                                           axh=res_h, foreground=foreground,
                                           background=background,
                                           parallel=parallel,
                                           smoothing_steps=smoothing_steps,
                                           mask=mask)
        for row in xrange(n_rows):
            for column in xrange(n_columns):
                ax = self._axes[row * n_columns + column]
                ax.imshow(ims[row][column])

        # time labels
        y = 0.25 / layout.h
        for i, label in enumerate(header):
            x = (0.5 + i) / layout.ncol
            self.figure.text(x, y, label, va='center', ha='center')

        ColorBarMixin.__init__(self, lambda: cmap_params, data)
        self._show()

    def _fill_toolbar(self, tb):
        ColorBarMixin._fill_toolbar(self, tb)


class BinTable(_BinTable):
    """DSPM plot bin-table"""
    def __init__(self, ndvar, tstart=None, tstop=None, tstep=0.1,
                 fmin=13, fmax=22, fmid=None,
                 surf='smoothwm', views=('lat', 'med'), hemi=None,
                 summary='sum', title=None, *args, **kwargs):
        im_func = partial(_dspm_bin_table_ims, fmin, fmax, fmid)
        _BinTable.__init__(self, ndvar, tstart, tstop, tstep, im_func, surf,
                           views, hemi, summary, title, *args, **kwargs)


class ClusterBinTable(_BinTable):
    """Data plotted on brain for different time bins and views

    Parameters
    ----------
    ndvar : NDVar (time x source)
        Data to be plotted.
    tstart : None | scalar
        Time point of the start of the first bin (inclusive; None to use the
        first time point in ndvar).
    tstop : None | scalar
        End of the last bin (exclusive; None to end with the last time point
        in ndvar).
    tstep : scalar
        Size of each bin (in seconds).
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : list of str
        Views to display (for each hemisphere, lh first). Options are:
        'rostral', 'parietal', 'frontal', 'ventral', 'lateral', 'caudal',
        'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both'
        Which hemispheres to plot (default based on data).
    summary : str
        How to summarize data in each time bin. Can be the name of a numpy
        function that takes an axis parameter (e.g., 'sum', 'mean', 'max') or
        'extrema' which selects the value with the maximum absolute value.
        Default is sum.
    vmax : scalar != 0
        Maximum value in the colormap. Default is the maximum value in the
        cluster.
    title : str
        Figure title.
    """
    def __init__(self, ndvar, tstart=None, tstop=None, tstep=0.1,
                 surf='smoothwm', views=('lat', 'med'), hemi=None,
                 summary='sum', vmax=None, title=None, *args, **kwargs):
        im_func = partial(_cluster_bin_table_ims, vmax)
        _BinTable.__init__(self, ndvar, tstart, tstop, tstep, im_func, surf,
                           views, hemi, summary, title, *args, **kwargs)


def dspm_bin_table(ndvar, fmin=2, fmax=8, fmid=None,
                   tstart=None, tstop=None, tstep=0.1, surf='smoothwm',
                   views=('lat', 'med'), hemi=None, summary='extrema',
                   axw=300, axh=250, *args, **kwargs):
    """Create a table with images for time bins

    Parameters
    ----------
    ndvar : NDVar (time x source)
        Data to be plotted.
    fmin, fmax : scalar >= 0
        Start- and end-point for the color gradient for positive values. The
        gradient for negative values goes from -fmin to -fmax. Values between
        -fmin and fmin are transparent.
    fmid : None | scalar
        Midpoint for the color gradient. If fmid is None (default) it is set
        half way between fmin and fmax.
    tstart : None | scalar
        Time point of the start of the first bin (inclusive; None to use the
        first time point in ndvar).
    tstop : None | scalar
        End of the last bin (exclusive; None to end with the last time point
        in ndvar).
    tstep : scalar
        Size of each bin (in seconds).
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : list of str
        Views to display (for each hemisphere, lh first). Options are:
        'rostral', 'parietal', 'frontal', 'ventral', 'lateral', 'caudal',
        'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both'
        Which hemispheres to plot (default based on data).
    summary : str
        How to summarize data in each time bin. Can be the name of a numpy
        function that takes an axis parameter (e.g., 'sum', 'mean', 'max') or
        'extrema' which selects the value with the maximum absolute value.
        Default is extrema.
    axw, axh : scalar
        Subplot width/height (default axw=300, axh=250).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    smoothing_steps : None | int
        Number of smoothing steps if data is spatially undersampled (pysurfer
        ``Brain.add_data()`` argument).
    mask : bool | matplotlib color
        Shade areas that are not in ``ndvar``. Can be matplotlib color,
        including alpha (e.g., ``(1, 1, 1, 0.5)`` for semi-transparent white).
    subjects_dir : None | str
        Override the subjects_dir associated with the source space dimension.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 


    Returns
    -------
    images : Image
        FMTXT Image object that can be saved as SVG or integrated into an
        FMTXT document.


    Notes
    -----
    Plotting is based on :func:`plot.brain.dspm`.

    The resulting image can be saved with either of the following (currently
    the only supported formats)::

    >>> image.save_html("name.html")
    >>> image.save_image("name.svg")


    See Also
    --------
    plot.brain.bin_table: plotting clusters as bin-table
    """
    data = ndvar.bin(tstep, tstart, tstop, summary)
    ims, header, _ = _dspm_bin_table_ims(fmin, fmax, fmid, data, surf, views,
                                         hemi, axw, axh, *args, **kwargs)
    return im_table(ims, header)


def bin_table(ndvar, tstart=None, tstop=None, tstep=0.1, surf='smoothwm',
              views=('lat', 'med'), hemi=None, summary='sum', vmax=None,
              axw=300, axh=250, *args, **kwargs):
    """Create a table with images for time bins

    Parameters
    ----------
    ndvar : NDVar (time x source)
        Data to be plotted.
    tstart : None | scalar
        Time point of the start of the first bin (inclusive; None to use the
        first time point in ndvar).
    tstop : None | scalar
        End of the last bin (exclusive; None to end with the last time point
        in ndvar).
    tstep : scalar
        Size of each bin (in seconds).
    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
        Freesurfer surface to use as brain geometry.
    views : list of str
        Views to display (for each hemisphere, lh first). Options are:
        'rostral', 'parietal', 'frontal', 'ventral', 'lateral', 'caudal',
        'medial', 'dorsal'.
    hemi : 'lh' | 'rh' | 'both'
        Which hemispheres to plot (default based on data).
    summary : str
        How to summarize data in each time bin. Can be the name of a numpy
        function that takes an axis parameter (e.g., 'sum', 'mean', 'max') or
        'extrema' which selects the value with the maximum absolute value.
        Default is sum.
    vmax : scalar != 0
        Maximum value in the colormap. Default is the maximum value in the
        cluster.
    out : 'image' | 'figure'
        Format in which to return the plot. ``'image'`` (default) returns an
        Image object that
    axw, axh : scalar
        Subplot width/height (default axw=300, axh=250).
    foreground : mayavi color
        Figure foreground color (i.e., the text color).
    background : mayavi color
        Figure background color.
    parallel : bool
        Set views to parallel projection (default ``True``).
    cortex : str | tuple | dict
        Mark gyri and sulci on the cortex. Presets: ``'classic'`` (default), 
        ``'high_contrast'``, ``'low_contrast'``, ``'bone'``. Can also be a 
        single color (e.g. ``'red'``, ``(0.1, 0.4, 1.)``) or a tuple of two 
        colors for gyri and sulci (e.g. ``['red', 'blue']`` or ``[(1, 0, 0), 
        (0, 0, 1)]``). For all options see the PySurfer documentation.
    smoothing_steps : None | int
        Number of smoothing steps if data is spatially undersampled (pysurfer
        ``Brain.add_data()`` argument).
    mask : bool | matplotlib color
        Shade areas that are not in ``ndvar``. Can be matplotlib color,
        including alpha (e.g., ``(1, 1, 1, 0.5)`` for semi-transparent white).
    subjects_dir : None | str
        Override the subjects_dir associated with the source space dimension.
    name : str
        Equivalent to ``title``, for consistency with other plotting functions. 


    Returns
    -------
    images : Image
        FMTXT Image object that can be saved as SVG or integrated into an
        FMTXT document.


    Notes
    -----
    Plotting is based on :func:`plot.brain.cluster`.

    The resulting image can be saved with either of the following (currently
    the only supported formats)::

    >>> image.save_html("name.html")
    >>> image.save_image("name.svg")


    See Also
    --------
    plot.brain.dspm_bin_table: plotting SPMs as bin-table
    """
    data = ndvar.bin(tstep, tstart, tstop, summary)
    ims, header, _ = _cluster_bin_table_ims(vmax, data, surf, views, hemi,
                                            axw, axh, *args, **kwargs)
    return im_table(ims, header)


def _dspm_bin_table_ims(fmin, fmax, fmid, data, surf, views, hemi, axw, axh,
                        *args, **kwargs):
    if fmax is None:
        fmax = max(data.max(), -data.min())

    def brain_(hemi_):
        return dspm(data, fmin, fmax, fmid, surf, views[0], hemi_, False, None,
                    axw, axh, *args, **kwargs)

    return _bin_table_ims(data, hemi, views, brain_)


def _cluster_bin_table_ims(vmax, data, surf, views, hemi, axw, axh, *args,
                           **kwargs):
    if vmax is None:
        vmax = max(-data.min(), data.max())
        if vmax == 0:
            raise NotImplementedError("The data of ndvar is all zeros")
    elif vmax == 0:
        raise ValueError("vmax can't be 0")
    elif vmax < 0:
        vmax = -vmax

    def brain_(hemi_):
        return cluster(data, vmax, surf, views[0], hemi_, False, None, axw,
                       axh, None, None, *args, **kwargs)

    return _bin_table_ims(data, hemi, views, brain_)


def _bin_table_ims(data, hemi, views, brain_func):
    if isinstance(views, basestring):
        views = (views,)
    ims = []
    if hemi is None:
        hemis = []
        if data.source.lh_n:
            hemis.append('lh')
        if data.source.rh_n:
            hemis.append('rh')
    elif hemi == 'both':
        hemis = ['lh', 'rh']
    elif hemi == 'lh' or hemi == 'rh':
        hemis = [hemi]
    else:
        raise ValueError("hemi=%s" % repr(hemi))

    cmap_params = None
    for hemi in hemis:
        brain = brain_func(hemi)

        hemi_lines = [[] for _ in views]
        for i in xrange(len(data.time)):
            brain.set_data_time_index(i)
            for line, view in izip(hemi_lines, views):
                brain.show_view(view)
                im = brain.screenshot_single('rgba', True)
                line.append(im)
        ims += hemi_lines
        if cmap_params is None:
            cmap_params = brain._get_cmap_params()
        brain.close()

    header = ['%i - %i ms' % (ms(t0), ms(t1)) for t0, t1 in data.info['bins']]
    return ims, header, cmap_params


class SequencePlotter(object):
    """Grid of anatomical images in one figure

    Examples
    --------
    Plotting an evoked response in 50 ms bins:

    >>> ndvar_binned = ndvar.bin(0.05, 0, 0.3, 'extrema')
    >>> sp = SequencePlotter()
    >>> sp.set_brain_args(surf='smoothwm')
    >>> sp.add_ndvar(ndvar_binned)
    >>> p = sp.plot_table(view='lateral')
    >>> p.save('Figure.pdf')
    """
    max_n_bins = 25

    def __init__(self):
        self._data = []
        self._source = None
        self._time = None
        self._bins = None
        self._brain_args = {}

    def set_brain_args(self, surf='inflated', foreground=None, background=None,
                       parallel=True, cortex='classic', mask=True):
        """Set parameters for anatomical plot

        For parameter descriptions see :func:`plot.brain.brain`.
        """
        self._brain_args = {
            'surf': surf, 'foreground': foreground, 'background': background,
            'parallel': parallel, 'cortex': cortex, 'mask': mask}

    def add_ndvar(self, ndvar, *args, **kwargs):
        """Add a data layer to the brain plot

        Multiple data layers can be added sequentially, but each additional
        layer needs to have a time dimension that is compatible with previous
        layers (or no time dimension).

        Parameters
        ----------
        ndvar : NDVar
            Data to add. ``Source`` dimension only for a static layer,
            additional ``time`` or ``case`` dimension for dynamic layers.
        ...
            :meth:`~plot._brain_object.Brain.add_ndvar` parameters.
        """
        source = ndvar.get_dim('source')
        if self._source is None:
            self._source = source
        elif source.subject != self._source.subject:
            raise ValueError("NDVar has different subject (%s) than previously "
                             "added data (%s)" %
                             (source.subject, self._source.subject))
        elif source.subjects_dir != self._source.subjects_dir:
            raise ValueError("NDVar has different subjects_dir (%s) than "
                             "previously added data (%s)" %
                             (source.subjects_dir, self._source.subjects_dir))

        if ndvar.has_dim('time'):
            time_dim = ndvar.time
        elif ndvar.has_case:
            time_dim = ndvar.dims[0]
        else:
            time_dim = None

        if time_dim is not None:
            if self._time is None:
                if len(time_dim) > self.max_n_bins:
                    raise ValueError(
                        "Trying to plot %s with %i bins. If this is intentional, "
                        "set SequencePlotter.max_n_bins to a larger value." %
                        (time_dim, len(time_dim)))
                self._time = time_dim
            elif time_dim != self._time:
                raise ValueError("New axis %s is incompatible with previously "
                                 "set axis %s" % (time_dim, self._time))

            if self._bins is None and 'bins' in ndvar.info:
                self._bins = ndvar.info['bins']

        self._data.append(('data', ndvar, args, kwargs))

    def _bin_labels(self):
        if self._bins is not None:
            return ['%i - %i ms' % (ms(t0), ms(t1)) for t0, t1 in self._bins]
        elif isinstance(self._time, UTS):
            return ['%i ms' % ms(t) for t in self._time]
        else:
            return False

    def plot_table(self, hemi=('lh', 'rh'), view=('lateral', 'medial'),
                   orientation='horizontal', column_header=True, *args, **kwargs):
        """Create a figure with the images

        Parameters
        ----------
        hemi : str | list of str
            Hemispheres to plot.
        view : str | list of {str | tuple}
            Views to plot. A view can be specified as a string, or as a tuple
            including parallel-view parameters ``(view, forward, up, scale)``,
            e.g., ``('lateral', 0, 10, 70)``.
        orientation : 'vertical' | 'horizontal'
            Direction of the time/case axis.
        column_header : bool | list of str
            Headers for columns of images (default is inferred from the data).
        ...
            Layout parameters for the figure.

        Returns
        -------
        fig : EelFigure
            Figure created by the plot.
        """
        if not self._data:
            raise RuntimeError("No data")
        hemis = (hemi,) if isinstance(hemi, basestring) else hemi
        if isinstance(view, basestring):
            views = (view,)
        elif len(view) > 1 and not isinstance(view[1], basestring):
            views = (view,)
        else:
            views = view

        n_views = len(hemis) * len(views)
        n_bins = 1 if self._time is None else len(self._time)
        if orientation == 'horizontal':
            n_columns = n_bins
            n_rows = n_views
            transpose = False
        elif orientation == 'vertical':
            n_columns = n_views
            n_rows = n_bins
            transpose = True
        else:
            raise ValueError("orientation=%r" % (orientation,))

        figure = ImageTable(n_rows, n_columns, *args, **kwargs)

        im_rows = []
        cmap_params = None
        cmap_data = None
        for hemi in hemis:
            hemi_rows = [[] for _ in views]

            # plot brain
            b = brain(self._source, hemi=hemi, views='lateral', w=figure._res_w,
                      h=figure._res_h, time_label='', **self._brain_args)
            # add data layers
            for layer, ndvar, args, kwargs in self._data:
                if layer == 'data':
                    b.add_ndvar(ndvar, *args, time_label='', **kwargs)
                else:
                    raise RuntimeError("%r data layer" % (layer,))
            b.set_parallel_view(scale=True)

            # capture images
            for i in xrange(n_bins):
                if self._time is not None:
                    b.set_data_time_index(i)
                for row, view in izip(hemi_rows, views):
                    if isinstance(view, basestring):
                        b.show_view(view)
                    else:
                        b.show_view(view[0])
                        b.set_parallel_view(*view[1:])
                    row.append(b.screenshot_single('rgba', True))
            im_rows += hemi_rows

            if cmap_params is None:
                cmap_params = b._get_cmap_params()
                cmap_data = ndvar
            b.close()

        if column_header is True and orientation == 'horizontal':
            column_header = self._bin_labels()

        if transpose:
            im_rows = zip(*im_rows)
        figure._add_ims(im_rows, column_header, cmap_params, cmap_data)
        return figure


def connectivity(source):
    """Plot source space connectivity

    Parameters
    ----------
    source : SourceSpace | NDVar
        Source space or NDVar containing the source space.

    Returns
    -------
    figure : mayavi Figure
        The figure.
    """
    from mayavi import mlab

    if isinstance(source, NDVar):
        source = source.get_dim('source')

    connections = source.connectivity()
    coords = source.coordinates
    x, y, z = coords.T

    figure = mlab.figure()
    src = mlab.pipeline.scalar_scatter(x, y, z, figure=figure)
    src.mlab_source.dataset.lines = connections
    lines = mlab.pipeline.stripper(src)
    mlab.pipeline.surface(lines, colormap='Accent', line_width=1, opacity=1.,
                          figure=figure)
    return figure


def copy(brain):
    "Copy the figure to the clip board"
    return brain.copy_screenshot()


def butterfly(y, cmap=None, vmin=None, vmax=None, hemi=None, name=None, h=2.5,
              w=5):
    u"""Shortcut for a Butterfly-plot with a time-linked brain plot

    Parameters
    ----------
    y : NDVar  ([case,] time, source)
        Data to plot; if ``y`` has a case dimension, the mean is plotted.
        ``y`` can also be a :mod:`~eelbrain.testnd` t-test result, in which
        case a masked parameter map is plotted (p ≤ 0.05).
    vmin : scalar
        Plot data range minimum.
    vmax : scalar
        Plot data range maximum.
    hemi : 'lh' | 'rh'
        Plot only this hemisphere (the default is to plot all hemispheres with
        data in ``y``).
    name : str
        The window title (default is y.name).
    h : scalar
        Plot height (inches).
    w : scalar
        Butterfly plot width (inches).

    Returns
    -------
    butterfly_plot : plot.Butterfly
        Butterfly plot.
    brain : Brain
        Brain plot.
    """
    import wx
    from .._stats import testnd
    from .._wxgui.mpl_canvas import CanvasFrame
    from ._brain_object import BRAIN_H, BRAIN_W
    from ._utsnd import Butterfly

    if isinstance(y, (testnd.ttest_1samp, testnd.ttest_rel, testnd.ttest_ind)):
        y = y.masked_parameter_map(0.05, name=y.Y)

    if name is None:
        name = y.name

    if y.has_case:
        y = y.mean('case')

    # find hemispheres to include
    if hemi is None:
        hemis = []
        if y.source.lh_n:
            hemis.append('lh')
        if y.source.rh_n:
            hemis.append('rh')
    elif hemi in ('lh', 'rh'):
        hemis = (hemi,)
    else:
        raise ValueError("hemi=%r" % (hemi,))

    # butterfly-plot
    plot_data = [y.sub(source=hemi_, name=hemi_.capitalize()) for hemi_ in hemis]
    p = Butterfly(plot_data, vmin=vmin, vmax=vmax,
                  h=h, w=w, ncol=1, name=name, color='black', ylabel=False)

    # position the brain window next to the butterfly-plot
    brain_h = h * p._layout.dpi
    if isinstance(p._frame, CanvasFrame):
        px, py = p._frame.GetPosition()
        pw, _ = p._frame.GetSize()
        display_w, _ = wx.DisplaySize()
        brain_w = int(brain_h * len(hemis) * BRAIN_W / BRAIN_H)
        brain_x = min(px + pw, display_w - brain_w)
        pos = (brain_x, py)
    else:
        pos = wx.DefaultPosition

    # Brain plot
    p_brain = brain(y, cmap, vmin, vmax, hemi=hemi, name=name, axh=brain_h,
                    mask=False, pos=pos)
    p.link_time_axis(p_brain)

    return p, p_brain
