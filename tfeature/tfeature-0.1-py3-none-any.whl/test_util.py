from tfeature import util
import pytest
import pandas as pd
from tdata import local


@pytest.fixture(scope='module')
def bar():
    return local.daily(
        '000001.SH', start_date=20141229, end_date=20171201
    ).loc[:, ['symbol', 'open', 'close', 'high', 'low', 'volume', 'turnover']]


@pytest.fixture(scope='module')
def removed_contains():
    return pd.read_csv(
        './tests/const/remove_contains.csv', index_col=0, parse_dates=True)


@pytest.fixture(scope='module')
def brush():
    return pd.read_csv(
        './tests/const/brush_macd_amount.csv', index_col=0, parse_dates=True)


def test_is_up(bar):
    assert not util.is_up(bar.loc['20171130', ['low', 'high']],
                          bar.loc['20171201', ['low', 'high']])
    assert util.is_up(bar.loc['20171128', ['low', 'high']],
                      bar.loc['20171129', ['low', 'high']])
    assert not util.is_up(bar.loc['20171127', ['low', 'high']],
                          bar.loc['20171128', ['low', 'high']])


def test_is_contain(bar):
    low_high = bar.loc[:, ['low', 'high']]
    assert not util.is_contain(low_high.loc['20171127'],
                               low_high.loc['20171128'])
    assert not util.is_contain(low_high.loc['20171128'],
                               low_high.loc['20171129'])
    assert util.is_contain(low_high.loc['20171129'], low_high.loc['20171130'])
    assert not util.is_contain(low_high.loc['20171130'],
                               low_high.loc['20171201'])


def test_contain(bar):
    low_high = bar.loc[:, ['low', 'high']]
    assert util.contain(
        *low_high.loc['20171128':'20171130'].values) == pytest.approx(
            (3306.28, 3343.06))
    assert util.contain(*low_high.loc['20171129':'20171201'].values) is None
    assert util.contain(*low_high.loc['20171124':'20171128'].values) is None
    assert util.contain(*low_high.loc['20171127':'20171129'].values) is None


def test_combine(bar, removed_contains):
    assert len(util.combine(bar)) == len(removed_contains)
    assert util.combine(bar).iat[9, 2] == pytest.approx(removed_contains.iat[9, 2])


def test_parting(removed_contains, brush):
    pt = util.parting(removed_contains)
    assert len(pt) == len(brush)
    assert pt.loc['2017-11-28', 'low'] == brush.loc['2017-11-28', 'low']
    assert pt.loc['2017-11-28', 'endpoint'] == brush.loc['2017-11-28',
                                                         'endpoint']


def test_hist_sum(bar, brush):
    hist_sum = util.hist_sum(bar)
    assert hist_sum.shape == brush.shape
    assert hist_sum.iloc[9, 8] == brush.iloc[9, 8]
    assert hist_sum.iloc[18, 8] == brush.iloc[18, 8]
