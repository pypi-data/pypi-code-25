from datasource.treasury import get_us_treasury_yield


def test_us_treasury():
    df = get_us_treasury_yield('2018-3-1', '2018-4-1', maturity='1y')
    assert len(df) > 0
    assert df.loc['2018-3-1'] is not None