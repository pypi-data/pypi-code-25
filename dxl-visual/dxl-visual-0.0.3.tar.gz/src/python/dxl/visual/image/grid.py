def grid_view(images, windows=None, scale=1.0, cmap=None,
              *,
              max_columns=None, max_rows=None,
              hide_axis=True,
              hspace=0.1, wspace=0.1, return_figure=False, dpi=None, adjust_figure_size=True, save_filename=None,
              invert_row_column=False,
              scale_factor=2.0,
              _top=None,
              _right=None):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.figure import SubplotParams
    """ subplot list of images of multiple categories into grid subplots

    Args:
        image_lists: list of [list of images or 4D tensor]
        windows: list of windows
        nb_column: columns of images
    Returns:
        Return figure if return_figure is true, else None.
    """
    images = _unified_images(images, invert_row_column)
    windows = _unified_windows(images, windows)
    images, windows = _adjust_images_to_fit_nb_columns(images, windows,
                                                       max_columns, max_rows)
    figsize, default_dpi = _adjust_figure_size(images, scale, scale_factor)
    from dxpy.debug.utils import dbgmsg
    dbgmsg(figsize, default_dpi)
    dbgmsg(images.shape)
    if dpi is None:
        dpi = default_dpi
    dpi = dpi * scale
    fig = plt.figure(figsize=figsize, dpi=dpi,
                     subplotpars=SubplotParams(left=0.0, right=1.0, bottom=0.0, top=1.0, wspace=0.0, hspace=0.0))
    # fig.subplots_adjust(hspace=hspace, wspace=wspace)
    nr, nc = images.shape
    if _top is None:
        # _top = figsize[1] / nr * nc
        _top = scale
    if _right is None:
        _right = figsize[0] / nc * nr
        _right = scale
    gs = gridspec.GridSpec(nr, nc,
                           wspace=wspace, hspace=hspace,
                           top=_top, bottom=0.0,
                           left=0.0, right=_right)
    for ir in range(nr):
        for ic in range(nc):
            if images[ir, ic] is None:
                continue
            # ax = plt.subplot(nr, nc, ir * nc + ic + 1)
            ax = plt.subplot(gs[ir, ic])
            ax.imshow(images[ir, ic], cmap=cmap,
                      vmin=windows[ir, ic, 0], vmax=windows[ir, ic, 1])
            if hide_axis:
                plt.axis('off')
            else:
                ax.set_xticklabels([])
                ax.set_yticklabels([])
    if save_filename is not None:
        fig.savefig(save_filename)
    if return_figure:
        return fig