from datasource.earning import get_earnings
import pandas as pd


def test_earning():
    df = get_earnings('MSFT')
    assert 'actual_eps' in df
    assert 'estimate_eps' in df
    assert 'period' in df
    assert 'timing' in df
    assert 'verified' in df

    earning_2018_q1 = df.loc[pd.to_datetime('2018-04-26')]
    assert earning_2018_q1['period'] == '2018Q1'
    assert earning_2018_q1['timing'] == 'AMC'
    assert earning_2018_q1['actual_eps'] == 0.95
    assert earning_2018_q1['estimate_eps'] == 0.85
