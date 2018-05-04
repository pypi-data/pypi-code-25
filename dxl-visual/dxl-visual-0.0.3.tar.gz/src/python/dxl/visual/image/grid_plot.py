import numpy as np
from typing import TypeVar


class PlotConfigContent:
    _config_dict = None
    _target_dict = None

    def __init__(self, cfg=None):
        if cfg is not None:
            self._pre_config_dict = self._config_dict
            self._config_dict = cfg

    def __enter__(self):
        pass


class PlotItem:
    def __init__(self,
                 start,
                 span,
                 content,
                 axis_type='line_bold',
                 axis_color='k',
                 fc='w',
                 **kw):
        self._s = start
        self._e = span
        self._c = content
        self._ac = axis_color
        self._axis_type = axis_type
        self._fc = fc

    def add_to_figure(self, fig, gs):
        slices = [slice(s, s + e) for s, e in zip(self._s, self._e)]
        ax = fig.add_subplot(gs[slices[0], slices[1]])
        for k in ax.spines:
            ax.spines[k].set_color(self._ac)
        ax.tick_params(axis='y', colors=self._ac)
        ax.tick_params(axis='x', colors=self._ac)
        ax.set_fc(self._fc)
        if self._axis_type == 'line':
            ax.set_xticks([])
            ax.set_yticks([])
        elif self._axis_type == 'line_bold':
            for k in ax.spines:
                ax.spines[k].set_linewidth(3.0)
            ax.set_yticks([])
            ax.set_xticks([])
        elif self._axis_type is None or self._axis_type == 'none':
            ax.set_axis_off()
        # TODO: Rework and seperate axis properties out
        # ax.spines['bottom'].set_color('#dddddd')
        # ax.spines['top'].set_color('#dddddd')
        # ax.spines['right'].set_color('red')
        # ax.spines['left'].set_color('red')
        return ax


class TextItem(PlotItem):
    def __init__(self, start, span, s, fontsize=16, rotation=0, tc='k', **kw):
        super().__init__(start, span, s, **kw)
        self._fontsize = fontsize
        self._rotation = rotation
        self._text_color = tc

    def add_to_figure(self, fig, gs):
        ax = super().add_to_figure(fig, gs)
        self._text = ax.text(
            0.5,
            0.5,
            self._c,
            va='center',
            ha='center',
            fontsize=self._fontsize,
            rotation=self._rotation,
            color=self._text_color)
        return ax


class ColorBarItem(PlotItem):
    def __init__(self,
                 start,
                 span,
                 img_item,
                 image_scale=256.0 * 1.414,
                 line_scale=100.0,
                 label="10 mm",
                 font_size=16,
                 line_width=3.0,
                 font_color='k',
                 no_line=False,
                 cbar_range=None,
                 force_int=True,
                 **kw):
        super().__init__(start, span, img_item, **kw)
        self._image_scale = image_scale
        self._line_scale = line_scale
        self._label = label
        self._fontsize = font_size
        self._fontcolor = font_color
        self._line_width = line_width
        self._no_line = no_line
        self._cbar_range = cbar_range
        self._force_int = force_int

    def _get_cbar_axes(self, fig, ax):
        bbox = ax.get_position()
        l, b, r, t = bbox.x0, bbox.y0, bbox.x1, bbox.y1
        w, h = r - l, t - b
        cb_l, cb_b = l + .6 * w, b + .2 * h
        cb_w, cb_h = .1 * w, .6 * h
        return fig.add_axes([cb_l, cb_b, cb_w, cb_h])

    def _add_line(self, ax):
        import matplotlib
        ratio = self._line_scale / self._image_scale
        x0, x1 = ax.get_xlim()[0], ax.get_xlim()[1]
        y0, y1 = ax.get_ylim()[0], ax.get_ylim()[1]
        scale_current = ((y1 - y0)**2.0 + (x1 - x0)**2.0)**0.5
        len_line = scale_current * ratio
        lx0 = .9 * x0 + (1 - .9) * x1
        lx1 = lx0 + len_line
        ly = .9 * y0 + (1 - .9) * y1
        l = matplotlib.lines.Line2D(
            [lx0, lx1], [ly, ly],
            linewidth=self._line_width,
            color=self._fontcolor)

        ax.add_line(l)
        ax.text(
            lx0 + .5 * len_line,
            ly + .05 * (y1 - y0),
            self._label,
            fontsize=self._fontsize,
            horizontalalignment='center',
            verticalalignment='bottom',
            color=self._fontcolor)

    def _add_colorbar(self, fig, ax):
        import matplotlib.pyplot as plt
        import numpy as np
        if self._cbar_range is None:
            vmin, vmax = self._c._img.get_clim()
        else:
            vmin, vmax = self._cbar_range
        if self._force_int:
            tks = np.linspace(vmin, vmax, 4).flatten()
            tks = ['{:3.0f}'.format(v) for v in tks]
            tks = [float(v) for v in tks]
            if tks[-1] > vmax:
                tks[-1] = vmax - (vmax - vmin) * 0.05
                tks[-1] = '{:3.0f}'.format(tks[-1])
                tks[-1] = float(tks[-1])
        else:
            tks = np.linspace(vmin, vmax, 3).flatten()
            tks = ['{:0.1f}'.format(v) for v in tks]
            tks = [float(v) for v in tks]
        cb = plt.colorbar(
            self._c._img, self._get_cbar_axes(fig, ax), ticks=tks)
        cb.ax.tick_params(labelsize=self._fontsize)
        cb.ax.tick_params(labelcolor=self._fontcolor)

    def add_to_figure(self, fig, gs):
        import matplotlib.pyplot as plt
        ax = super().add_to_figure(fig, gs)
        self._add_colorbar(fig, ax)
        if not self._no_line:
            self._add_line(ax)
        return ax


class ImageItem(PlotItem):
    def __init__(self, start, span, image, window=None, cmap=None, **kw):
        super().__init__(start, span, image, **kw)
        self._window = window
        self._cmap = cmap

    def add_to_figure(self, fig, gs):
        ax = super().add_to_figure(fig, gs)
        if self._window is None:
            vmin, vmax = None, None
        else:
            vmin, vmax = self._window
        self._img = ax.imshow(
            self._c, cmap=self._cmap, aspect='auto', vmin=vmin, vmax=vmax)
        return ax


class ImageZoomItem(ImageItem):
    def __init__(self, slicer, grids=(3, 3), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._slicer = slicer
        self._grids = grids

    def _get_mini_img_ax(self, fig, ax, irow, icol):
        bbox = ax.get_position()
        l, b, r, t = bbox.x0, bbox.y0, bbox.x1, bbox.y1
        sx, sy = (r - l) / self._grids[1], (t - b) / self._grids[0]
        return fig.add_axes([l + sx * icol, b + sy * irow, sx, sy])

    def _add_mini_imgs(self, fig, ax):
        mini_imgs = self._slicer(self._c)
        for i, row in enumerate(mini_imgs):
            for j, v in enumerate(row):
                if v is None:
                    continue
                ax_mini = self._get_mini_img_ax(fig, ax)
                ax.imshow(
                    v, cmap=self._cmap, aspect='auto', vmin=vmin, vmax=vmax)

    def add_to_figure(self, fig, gs):
        ax = super().add_to_figure(fig, gs)
        return ax


def grid_plot(nb_row,
              nb_column,
              items,
              scale=1,
              output=None,
              grid_spec=None,
              dpi=80,
              hspace=0.01,
              wspace=0.01):
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    fig = plt.figure(
        figsize=(nb_column * scale, nb_row * scale), frameon=False)
    if grid_spec is None:
        gs = GridSpec(
            nb_row,
            nb_column,
            top=1.0,
            bottom=0.0,
            left=0.0,
            right=1.0,
            hspace=hspace,
            wspace=wspace)
    else:
        gs = grid_spec
    for it in items:
        it.add_to_figure(fig, gs)
    if output is not None:
        plt.savefig(output, dpi=dpi)
    return fig


def profiles(images, sample_points, window=None, cmap=None):
    grid_x, grid_y = np.mgrid[0:images.shape[0]:images.shape[0], 0:
                              images.shape[1]:images.shape[1]]


def plot_profile(image,
                 ax,
                 points,
                 method='points',
                 show_image=True,
                 image_size=None,
                 image_offset=None,
                 image_kwargs=None,
                 line_kwargs=None,
                 profile_kwargs=None,
                 plot_line_kwargs=None):
    from ..reduce import profile, profile_h, profile_v
    import matplotlib as mpl

    fig = ax.figure
    xb, yb = ax.get_xbound(), ax.get_ybound()
    p = ax.get_position()
    l, b, w, h = p.x0, p.y0, p.x1 - p.x0, p.y1 - p.y0
    if image_size is None:
        image_size = (.4, .4)
    if image_offset is None:
        image_offset = (.0, .5)
    l, b = l + image_offset[0] * w, b + image_offset[1] * h
    w, h = image_size[0] * w, image_size[1] * h
    if profile_kwargs is None:
        profile_kwargs = dict()
    if plot_line_kwargs is None:
        plot_line_kwargs = dict()
    if method == 'points':
        v = profile(image, points, **profile_kwargs)
        p = (points[:, 0], points[:, 1])
        hl = ax.plot(np.arange(0, len(v)), v, **plot_line_kwargs)
    elif method == 'h':
        v, p = profile_h(image, points, **profile_kwargs)
        hl = ax.plot(p[0], v, **plot_line_kwargs)
    elif method == 'v':
        v, p = profile_v(image, points, **profile_kwargs)
        hl = ax.plot(p[1], v, **plot_line_kwargs)
    if show_image:
        if image_kwargs is None:
            image_kwargs = dict()
        if line_kwargs is None:
            line_kwargs = dict()
        imgax = fig.add_axes([l, b, w, h], frameon=False)
        imgax.set_axis_off()
        imgax.imshow(image, **image_kwargs)
        l = mpl.lines.Line2D(p[0], p[1], **line_kwargs)
        imgax.add_line(l)
        return hl, imgax
    return hl
