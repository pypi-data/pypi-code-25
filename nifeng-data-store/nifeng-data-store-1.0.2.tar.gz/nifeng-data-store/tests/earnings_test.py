from datetime import datetime
from unittest import mock

from app.earnings import earnings_service, earnings_repository
from app.earnings.earnings_model import EarningsModel
from app.foundation.constants import constant


@mock.patch.object(earnings_repository, 'get_earnings_statistics')
def test_should_return_empty_if_no_currency_found(get_earnings_statistics):
    get_earnings_statistics.return_value = None

    is_success, history_earnings, description = earnings_service.get_history_earnings('client_no-foo', 'currency-foo',
                                                                                      '2018-03-01', '2018-03-30')

    assert is_success is True
    assert description is constant.NO_EARNINGS_WAS_FOUND
    assert history_earnings is None


@mock.patch.object(earnings_repository, 'get_earnings_statistics')
def test_should_return_history_earnings(get_earnings_statistics):
    expected_earnings_models = []
    earnings_model = EarningsModel()
    earnings_model.earning = 0.300000
    earnings_model.create_time = datetime.strptime('2018-03-30', '%Y-%m-%d')
    expected_earnings_models.append(earnings_model)
    get_earnings_statistics.return_value = expected_earnings_models

    is_success, history_earnings, description = earnings_service.get_history_earnings('client_no-foo', 'BTC',
                                                                                      '2018-03-01', '2018-03-30')

    assert is_success is True
    assert history_earnings.currency == 'BTC'
    assert history_earnings.earnings[0].date.strftime('%Y-%m-%d') == '2018-03-30'
    assert history_earnings.earnings[0].earning is 0.300000
    assert history_earnings.period.start_date == '2018-03-01'
    assert history_earnings.period.end_date == '2018-03-30'
