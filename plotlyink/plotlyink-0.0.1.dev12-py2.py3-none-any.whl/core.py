import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd

from .config import run_from_ipython, run_from_jupyter
from .utils import kwargshandler
from .colors import to_rgba


class BasePlotMethods():
    """
    Base class for assembling a pandas plot using plotly.

    Args:
        data (pd.DataFrame):
    """

    @property
    def _kind(self):
        """Specify kind str. Must be overridden in child class"""
        raise NotImplementedError

    def __init__(self, data):
        self._data = data

    def _figure_handler(self, fig, as_figure, as_image, as_url):
        """Handle what to do with plotly fig."""
        if not any([as_figure, as_image, as_url]):
            if run_from_ipython():
                if run_from_jupyter():
                    plotly.offline.init_notebook_mode()
                    return plotly.offline.iplot(fig)
                else:
                    return plotly.offline.plot(fig)
            else:
                return fig

        if as_figure:
            return fig
        elif as_image:
            raise NotImplementedError
        elif as_url:
            raise NotImplementedError

    def _get_figure(self, kind, **kwargs):
        raise NotImplementedError

    def __call__(self, mode=None, as_figure=False, as_image=False, as_url=False,
                 **kwargs):
        fig = self._get_figure(mode=mode, **kwargs)
        return self._figure_handler(
            fig=fig, as_figure=as_figure, as_image=as_image, as_url=as_url)


class ScatterPlot(BasePlotMethods):
    _kind = 'scatter'

    def _get_figure(self, mode='line', fill=False, **kwargs):
        """
        Args:
            mode (str): within ['line', 'markers', 'area']
            fill (bool): has effect only for mode == 'line'
        """
        x = self._data.index
        y = self._data.columns

        colors = kwargshandler.colors(self._data, **kwargs)
        fig = go.Figure()

        for col in y:
            t = go.Scatter(x=x, y=self._data[col], name=col)
            t['marker']['color'] = colors[col]

            if mode == 'line':
                t.update({'mode': 'line'})
                if fill:
                    t.update({'fill': 'tozeroy',
                              'fillcolor': to_rgba(colors[col], 0.3)})

            elif mode == 'area':
                t.update({'mode': 'line',
                          'fill': 'tonexty',
                          'fillcolor': to_rgba(colors[col], 0.3)})

            elif mode == 'markers':
                t.update({'mode': 'markers',
                          'marker': {'size': 10}})

            fig['data'].append(t)

        fig['layout'].update(kwargshandler.layout(**kwargs))

        return fig

    def line(self, fill=False, **kwargs):
        return self(mode='line', fill=fill, **kwargs)

    def area(self, **kwargs):
        return self(mode='area', **kwargs)

    def markers(self, **kwargs):
        return self(mode='markers', **kwargs)


class BarPLot(BasePlotMethods):
    _kind = 'bar'

    def _get_figure(self, mode='vertical', **kwargs):
        """
        Args:
            mode (str): within ['vertical', 'horizontal'].
        """
        x = self._data.index
        y = self._data.columns

        colors = kwargshandler.colors(self._data, **kwargs)
        fig = go.Figure()

        for col in y:
            t = go.Bar(x=x, y=self._data[col], name=col)
            t['marker']['color'] = colors[col]
            fig['data'].append(t)

        fig['layout'].update(kwargshandler.layout(**kwargs))

        if mode.lower() in ['horizontal', 'h']:
            fig['data'].update(dict(orientation='h'))

        return fig

    def bar(self, **kwargs):
        return self(mode='vertical', **kwargs)

    def hbar(self, **kwargs):
        return self(mode='horizontal', **kwargs)


class HeatMap(BasePlotMethods):
    _kind = 'heatmap'

    _data = None

    def _get_figure(self, zmin=None, zmax=None, **kwargs):
        """"""
        x = self._data.index
        y = self._data.columns
        z = self._data.values.transpose()

        # values min & max:
        zmin = zmin if zmin else z[~np.isnan(z)].min()
        zmax = zmax if zmax else z[~np.isnan(z)].max()

        # Colors handle for heatmap a little bit different.
        colors = kwargshandler.colors(self._data, **kwargs)
        colorscale = []
        for i, key in enumerate(colors):
            colorscale.append([float(i)/len(colors), colors[key]])

        # Greys, YlGnBu, Greens, YlOrRd, Bluered, RdBu, Reds, Blues, Picnic,
        # Rainbow, Portland, Jet, Hot, Blackbody, Earth, Electric, Viridis, Cividis

        heatmap = go.Heatmap(x=x.tolist(), y=y.tolist(), z=z.tolist(),
                             zmin=zmin, zmax=zmax,
                             colorscale=colorscale,
                             )

        layout = kwargshandler.layout(**kwargs)
        heatmap.update(kwargshandler.heatmap(**kwargs))
        return {'data': [heatmap], 'layout': layout}
