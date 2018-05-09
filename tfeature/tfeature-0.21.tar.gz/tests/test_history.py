import pytest
from .context import zen
from zen.history_view import HistoryView
import zen.data_proxy as data


@pytest.fixture(scope='module')
def hist_df():
    return data.get_local_data(
        '000001', asset='INDEX', start='20141229', end='20171201')


@pytest.fixture(scope='module')
def removed_contains():
    return pd.read_csv(
        './tests/const/remove_contains.csv', index_col=0, parse_dates=True)


@pytest.fixture(scope='module')
def brush():
    return pd.read_csv(
        './tests/const/brush_macd_amount.csv', index_col=0, parse_dates=True)

