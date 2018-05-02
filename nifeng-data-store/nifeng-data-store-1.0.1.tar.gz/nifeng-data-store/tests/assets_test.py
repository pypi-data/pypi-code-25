import json
from unittest import mock

from app.assets import assets_repository
from app.assets import assets_service
from app.assets.asset_model import AssetModel
from app.assets.asset_summary_model import AssetsSummaryModel
from app.assets.builder.AssetModelBuilder import AssetModelBuilder
from app.foundation.constants import constant


@mock.patch.object(assets_repository, 'get_assets_summary')
def test_should_return_asset_summary(get_assets_summary):
    assets_summary_model = AssetsSummaryModel()
    assets_summary_model.client_no = 'client-no-foo'
    assets_summary_model.currencies = {"as_btc": 1.5, "as_usd": 1.6}
    assets_summary_model.reference_no = '1521180097'
    assets_summary_model.clearing_time = '2018-03-16 06:01:44'

    get_assets_summary.return_value = assets_summary_model

    is_success, asset_summary_result, description = assets_service.get_assets_summary(None)

    assert is_success is True
    assert asset_summary_result.currencies["as_btc"] == 1.5
    assert asset_summary_result.currencies["as_usd"] == 1.6
    assert asset_summary_result.reference_no is '1521180097'
    assert asset_summary_result.clearing_time is '2018-03-16 06:01:44'


@mock.patch.object(assets_repository, 'get_assets_summary')
def test_should_return_empty_total_assets_amount_if_no_assets_was_found(get_assets_summary):
    get_assets_summary.return_value = None

    is_success, assets_summary_result, description = assets_service.get_assets_summary(None)

    assert is_success is True

    currencies = json.loads(assets_summary_result.currencies)
    assert currencies["as_btc"] == 0.0
    assert currencies["as_usd"] == 0.0
    assert description is constant.NO_ASSET_SUMMARY_WAS_FOUND
    assert assets_summary_result.reference_no is None
    assert assets_summary_result.clearing_time is None


@mock.patch.object(assets_repository, 'get_asset_models')
def test_should_return_assets(get_asset_models):
    given_client_no = 'client-no-foo'
    expected_asset_models = []
    asset_model = AssetModelBuilder() \
        .with_currency('BTC') \
        .with_origin_balance(0.6) \
        .with_current_balance(0.8) \
        .with_as_btc(0.8) \
        .with_as_usd(7735.03) \
        .with_reference_no('1234567') \
        .end()

    expected_asset_models.append(asset_model)
    get_asset_models.return_value = expected_asset_models

    is_success, assets_result, description = assets_service.get_assets(given_client_no)

    assert is_success is True
    assert len(assets_result) == 1

    first_asset = assets_result[0]
    assert first_asset.currency is 'BTC'
    assert first_asset.origin_balance == 0.600000
    assert first_asset.current_balance == 0.800000
    assert first_asset.earnings == 0.200000
    assert first_asset.roa == 33.33
    assert first_asset.as_usd == 7735.03
    assert first_asset.reference_no is '1234567'


@mock.patch.object(assets_repository, 'get_asset_models')
def test_should_return_empty_assets_if_no_assets_was_found(get_asset_models):
    get_asset_models.return_value = None

    is_success, assets_result, description = assets_service.get_assets(None)

    assert is_success is True
    assert not assets_result
    assert description is constant.NO_ASSETS_WAS_FOUND


@mock.patch.object(assets_repository, 'get_currencies')
def test_should_return_empty_currencies_if_no_currencies_were_found(get_currencies):
    get_currencies.return_value = None

    is_success, currencies, description = assets_service.get_currencies(None)

    assert is_success is True
    assert not currencies
    assert description is constant.NO_CURRENCIES_WERE_FOUND


@mock.patch.object(assets_repository, 'get_currencies')
def test_should_return_currencies(get_currencies):
    expected_currency_models = []
    currency_model = AssetModel()
    currency_model.currency = 'BTC'
    expected_currency_models.append(currency_model)
    get_currencies.return_value = expected_currency_models

    is_success, currencies, description = assets_service.get_currencies('client_no-foo')

    assert is_success is True
    assert currencies[0].name is 'BTC'
