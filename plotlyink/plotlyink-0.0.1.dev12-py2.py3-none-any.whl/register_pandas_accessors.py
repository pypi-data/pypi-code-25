import pandas as pd
import plotly.graph_objs as go
from .core import ScatterPlot, BarPLot, HeatMap


@pd.api.extensions.register_dataframe_accessor("iplot")
class FrameIplotMethods():
    """DataFrame interactive plotting accessor and method

    Examples
    --------
    >>> df.iplot.scatter.line()
    >>> df.iplot.scatter.line(fill=True)
    >>> df.iplot.scatter.area()

    These plotting methods can also be accessed by calling the accessor as a
    method with the ``kind`` argument:
    ``df.plot(kind='line')`` is equivalent to ``df.plot.line()``
    """

    def __init__(self, data):
        self._data = data

        # Scatter plots:
        self.scatter = ScatterPlot(data)

        # Bar plots:
        self._bar = BarPLot(data)
        self.bar = self._bar.bar
        self.hbar = self._bar.hbar

        # Heatmap plots:
        self.heatmap = HeatMap(data)

    def __call__(self, x=None, y=None, kind='scatter', mode='lines', **kwargs):
        return self.__dict__[kind](x=x, y=y, mode=mode)

    def missing_values(self, **kwargs):
        """Get an overview of missing values."""
        df = self._data.isna().astype(int)
        kwargs_updated = dict(
            zmin=0, zmax=1,
            colors='reds', ncolors=9,
            showscale = False,
            xgap=3, ygap=3,
            showgrid=False, zeroline=False)
        kwargs_updated.update(kwargs)
        return df.iplot.heatmap(**kwargs_updated)

    def correlation_matrix(self, **kwargs):
        """Plot the Correlation Matrix."""
        df = self._data.corr()
        kwargs_updated = dict(
            zmin=-1, zmax=1,
            colors='rdbu', ncolors=9,
            xgap=3, ygap=3, dtick=1,
            showgrid=False, zeroline=False,

            # square for 1920x1080 screens in awating for better plotly option
            yaxis = {'domain': [0, 1]},
            xaxis = {'domain': [0.28215, 1-0.28215]},
            colorbar = {'x': 1-0.22},
        )
        kwargs_updated.update(kwargs)
        return df.iplot.heatmap(**kwargs_updated)
