from datasource import equity_list


def test_sp500_list():
    sp500 = equity_list.get_sp500_list()
    assert len(sp500) >= 500
    for item in sp500:
        assert 'symbol' in item
        assert 'name' in item
        assert 'sector' in item


def test_nasdaq100_list():
    nasdaq100 = equity_list.get_nasdaq100_list()
    assert len(nasdaq100) >= 100
    for item in nasdaq100:
        assert 'name' in item
        assert 'symbol' in item

