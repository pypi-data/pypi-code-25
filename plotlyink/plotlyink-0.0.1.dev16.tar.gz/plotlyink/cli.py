from pathlib import Path
import plotly
import fire
import pandas as pd

from .register_pandas_accessors import FrameIplotMethods

DATA_DIR = Path(__file__).parent.parent / 'test/samples'


class CmdLine():

    def __init__(self):
        self.df = pd.read_csv(DATA_DIR / 'hurricanes.csv', index_col=0)

    def scatter(self, line=True, lineFill=True, area=True, markers=True):
        if line:
            fig = self.df.iplot.scatter.line(asFigure=True)
            plotly.offline.plot(fig, filename='/tmp/test_scatter_line.html')

        if lineFill:
            fig = self.df.iplot.scatter.line(fill=True, asFigure=True)
            plotly.offline.plot(fig, filename='/tmp/test_scatter_lineFill.html')

        if area:
            fig = self.df.iplot.scatter.area(asFigure=True)
            plotly.offline.plot(fig, filename='/tmp/test_scatter_area.html')

        if markers:
            fig = self.df.iplot.scatter.markers(asFigure=True)
            plotly.offline.plot(fig, filename='/tmp/test_scatter_markers.html')

    def heatmap(self, corrmat=True, misval=True):
        if corrmat:
            fig = self.df.iplot.heatmap.correlation_matrix(asFigure=True)
            plotly.offline.plot(fig, filename='/tmp/test_correlation_matrix.html')

        if misval:
            fig = self.df.iplot.heatmap.missing_values(asFigure=True)
            plotly.offline.plot(fig, filename='/tmp/test_missing_vals.html')


def main():
    fire.Fire(CmdLine)


if __name__ == '__main__':
    main()
