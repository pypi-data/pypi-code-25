from matplotlib.animation import FFMpegWriter
import matplotlib.pyplot as plt
from IPython.display import HTML

from .resample import between_rows, num_only


def update_figure(df1, n, autoscale=False, ax=None, axis=0, grayed=None, j=0, kind=None, rx=None, ry=None,
                  start=0, title=None):
    """ update_figure.

    Recalculates the whole plot for frame n.

    :param df1: pandas dataframe, required
    :param n: frame to render, required
    :param autoscale: bool, if True will adjust the scale as data is processed, else will pre-render full scale
    :param ax: matplotlib ax
    :param axis: 0 or 1 for horizontal or vertical data
    :param grayed: grayed out "background" data
    :param j: this is used to calculate if we are dealing with an even or odd data series, for color selection.
    :param kind: pandas plot kind
    :param rx: remove x axis
    :param ry: remove y axis
    :param start: will be used in 0.3 for offset
    :param title: optional, title for the plot
    :return: affects ax
    """
    if j%2:
        c0 = 'C0'
        c1 = 'C1'
    else:
        c0 = 'C1'
        c1 = 'C0'
    if kind == None:
        kind='line'
    items = df1.shape[0]
    ax.cla()
    if title is not None:
        ax.set_title(title)

    if grayed is not None:
        for row in range(grayed.shape[0]-1):
            grayed.iloc[row].plot(ax=ax, color='k', alpha=0.25)
    if axis:
        if not autoscale:
            df1.iloc[items - 1:items, ].plot(ax=ax, color=c0)
        df1.iloc[:n,].plot(ax=ax, color=c0, kind=kind)
    else:
        df1.iloc[0].plot(ax=ax, color=c0, alpha=0.25, kind=kind)
        df1.iloc[items - 1].plot(ax=ax, color=c1, alpha=0.25, kind=kind)
        if n >= items / 2:
            df1.iloc[n].plot(ax=ax, color=c1, kind=kind)
        else:
            df1.iloc[n].plot(ax=ax, color=c0, kind=kind)
    if title is not None:
        ax.legend().set_visible(False)
        plt.box(on=None)

    if rx:
        ax.axes.get_xaxis().set_visible(False)
    if ry:
        ax.axes.get_yaxis().set_visible(False)


def ianimate(df, autoscale=True, ax=None, axis=0, filename=None, fps=5, kind=None,  n=None, rx=None, ry=None,
             step=1, title=None):
    """ ianimate.

    Animate plots, output to jupyter notebook.

    :param df: pandas dataframe
    :param autoscale: bool, if True will adjust the scale as data is processed, else will pre-render full scale
    :param ax: matplotlib ax
    :param axis: 0 or 1 for horizontal or vertical data
    :param filename: file name to save the mp4 file to
    :param fps: frames per second - defaults to 5
    :param kind: pandas plot kind
    :param n: frame to render
    :param rx: remove x axis
    :param ry: remove y axis
    :param step: how many steps between frames
    :param title: optional, title for the plot
    :return: HTML video control widget for jupyter notebook
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_fig()

    if filename==None:
        filename='tmp.mp4'
    if n is None:
        n = df.shape[0]
    moviewriter = FFMpegWriter(fps=fps)
    with moviewriter.saving(fig, filename, dpi=100):
        for j in range(1, n, step):
            update_figure(df, n=j, ax=ax, axis=axis, autoscale=autoscale, kind=kind, rx=rx, ry=ry, title=title)
            moviewriter.grab_frame()
    return HTML(
        """
            <video width="640" height="480" controls loop>
              <source src="{}" type="video/mp4">
            </video>
        """.format(filename)
    )


def animate(df, filename, autoscale=True, ax=None, axis=0, fps=5, kind=None, n=None, rx=None, ry=None,
            step=1, title=None):
    """ animate.

    Animate plots and save to mp4 video.
    :param df: pandas dataframe, required
    :param filename: file name to save the mp4 file to, required
    :param autoscale: bool, if True will adjust the scale as data is processed, else will pre-render full scale
    :param ax: matplotlib ax
    :param axis: 0 or 1 for horizontal or vertical data
    :param fps: frames per second - defaults to 5
    :param kind: pandas plot kind
    :param n: frame to render
    :param rx: remove x axis
    :param ry: remove y axis
    :param step: how many steps between frames
    :param title: optional, title for the plot
    :return: N/A
    """
    ianimate(df=df, filename=filename,
             autoscale=autoscale, ax=ax, axis=axis, fps=fps, kind=kind,
             n=n, rx=rx, ry=ry, step=step, title=title)


def tweening(df, filename, autoscale=True, axis=0, fps=5, kind=None, rx=None, ry=None,
             step=1, title=None, transitions=10):
    """ tweening.

    :param df: pandas dataframe, required
    :param filename: file name to save the mp4 file to, required
    :param autoscale: bool, if True will adjust the scale as data is processed, else will pre-render full scale
    :param axis: 0 or 1 for horizontal or vertical data
    :param fps: frames per second - defaults to 5
    :param kind: pandas plot kind
    :param rx: remove x axis
    :param ry: remove y axis
    :param step: how many steps between frames
    :param title: optional, title for the plot
    :param transitions: how many interimary values to generate
    :return: HTML video control widget for jupyter notebook
    """

    fig, ax = plt.subplots()
    nb_data_points = df.shape[0]
    moviewriter = FFMpegWriter(fps=fps)
    grayed = num_only(df)
    with moviewriter.saving(fig, filename, dpi=100):
        for j in range(0, nb_data_points-1, step):
            dfj = df.iloc[j:]
            df_expanded = between_rows(dfj, n=transitions)
            for i in range(transitions):
                update_figure(df_expanded, n=i, ax=ax, axis=axis, autoscale=autoscale, grayed=grayed, j=j,
                              kind=kind, rx=rx, ry=ry, title=title)
                moviewriter.grab_frame()
    return HTML(
        """
            <video width="640" height="480" controls loop>
              <source src="{}" type="video/mp4">
            </video>
        """.format(filename)
    )
