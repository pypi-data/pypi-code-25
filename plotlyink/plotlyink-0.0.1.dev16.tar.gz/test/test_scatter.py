import plotlyink


def test_scatter_lines(dataset):
    fig = dataset.iplot.scatter()
    assert 'layout' in fig.keys()
    assert 'data' in fig.keys()
