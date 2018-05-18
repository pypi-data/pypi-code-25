import jpy
import figurewrapper


def figure(*args):
    return figurewrapper.FigureWrapper(args)


def plot(seriesname, *args):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.plot(seriesname, *args)


def catPlot(seriesname, *args):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.catPlot(seriesname, *args)


def ohlcPlot(seriesname, *args):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.ohlcPlot(seriesname, *args)


def histPlot(seriesname, *args):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.histPlot(seriesname, *args)


def catHistPlot(seriesname, *args):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.catHistPlot(seriesname, *args)


def piePlot(seriesname, *args):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.piePlot(seriesname, *args)


def plotBy(seriesname, table, xcol, ycol, byColumns):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.plotBy(seriesname, table, xcol, ycol, byColumns)


def catPlotBy(seriesname, table, xcol, ycol, byColumns):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.catPlotBy(seriesname, table, xcol, ycol, byColumns)


def ohlcPlotBy(seriesname, table, time, open, high, low, close, byColumns):
    figure_ = figurewrapper.FigureWrapper(None)
    return figure_.ohlcPlotBy(
        seriesname,
        table,
        time,
        open,
        high,
        low,
        close,
        byColumns)


@staticmethod
def oneClick(table, *args):
    numargs = len(args)
    if numargs < 1:
        raise ValueError('No columns specified')
    stringarray = figurewrapper.__create_java_array__(args)
    plottingconvenience = jpy.get_type(
        "com.illumon.iris.db.plot.PlottingConvenience")
    return plottingconvenience.oneClick(table, stringarray)
