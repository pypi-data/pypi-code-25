from datasource.price import get_historical


def assert_ohlc_df(df):
    assert 'open' in df
    assert 'high' in df
    assert 'low' in df
    assert 'close' in df
    assert 'volume' in df


def test_historical():
    latest_data = get_historical('SPY')
    assert len(latest_data) == 1
    assert_ohlc_df(latest_data)

    period_data = get_historical('QQQ', '2010-1-1', '2018-1-1', 'monthly')
    print(period_data)
    assert_ohlc_df(latest_data)
