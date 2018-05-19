from collections import namedtuple
import plotly.graph_objs as go
from .colors import to_plotly_colors_dict


def kwargs2dict(kwargs, keys):
    """
    Simple function that construct a dictionnary with keys if is in kwargs.
    """
    out = {}
    for k in keys:
        if k in kwargs:
            out[k] = kwargs[k]

    return out


def retrieve_colors_kwargs(data, **kwargs):
    """Construct dict based on valid kwargs for colors."""
    colors_kwargs = kwargs2dict(kwargs, ["colors", "ncolors", "filter_brightness"])
    return to_plotly_colors_dict(data.columns, **colors_kwargs)


def retrieve_layout_kwargs(**kwargs):
    """Construct dict based on valid kwargs keys for Layout."""
    base_layout = kwargs2dict(kwargs, dir(go.Layout()))
    xaxis = kwargs2dict(kwargs, dir(go.XAxis()))
    yaxis = kwargs2dict(kwargs, dir(go.YAxis()))

    if 'xaxis' in kwargs:
        xaxis.update(kwargs['xaxis'])
    if 'yaxis' in kwargs:
        yaxis.update(kwargs['yaxis'])

    base_layout.update({'xaxis': xaxis})
    base_layout.update({'yaxis': yaxis})
    return base_layout


def retrieve_heatmap_kwargs(**kwargs):
    lst_keys_heatmap = dir(go.Heatmap())
    lst_keys_heatmap = set(lst_keys_heatmap) - set(dir(go.Layout()))
    return kwargs2dict(kwargs, lst_keys_heatmap)


KwargsOptions = namedtuple('KwargsOptions', ['colors', 'layout', 'heatmap'])

kwargshandler = KwargsOptions(colors=retrieve_colors_kwargs,
                              layout=retrieve_layout_kwargs,
                              heatmap=retrieve_heatmap_kwargs,
                              )
