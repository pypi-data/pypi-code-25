from datetime import date
from swagger_client.mercury.client.api.marketdata_api import MarketdataApi
from swagger_client.utils import Utils


class TestUtils:
    def __init__(self):
        self.api = MarketdataApi()

    def create_single_option_position(self, opening_date):
        from swagger_client.mercury.client.model import OptionSingle, Position

        name = "SPX"
        data = {'is_call': True,
                'from_strike': 0.3,
                'to_strike': 0.5,
                'date': date(2018, 4, 9),
                'expiration': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)
        option_contract = option_chain.contracts[0]
        option_single = OptionSingle(symbol='SPX',
                                     direction='LONG',
                                     quantity=1,
                                     opening_date=opening_date,
                                     type='single',
                                     option_contract=option_contract)
        position = Position(trades=[option_single])
        return position

    def create_long_call_vertical_spread_position(self, opening_date):
        from swagger_client.mercury.client.model import \
            LongCallVerticalSpread, Position

        name = "SPX"
        data = {'is_call': True,
                'from_strike': 2625.0,
                'to_strike': 2665.0,
                'date': date(2018, 4, 9),
                'expiration': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_strike(
            name, **data)
        option_contracts = option_chain.contracts
        long_leg = Utils.create_option_leg_with_option_contract(
            option_contract=option_contracts[0],
            direction='LONG',
            quantity=1)
        short_leg = Utils.create_option_leg_with_option_contract(
            option_contract=option_contracts[-1],
            direction='SHORT',
            quantity=1)
        long_call_vertical_spread = LongCallVerticalSpread(
            symbol='SPX',
            opening_date=opening_date,
            quantity=1,
            short_leg=short_leg,
            long_leg=long_leg)
        position = Position(trades=[long_call_vertical_spread])
        return position

    def create_long_put_butterfly_position(self, opening_date):
        from swagger_client.mercury.client.model import \
            Butterfly, Position

        name = "SPX"
        data = {'is_call': False,
                'from_strike': 0.-0.5,
                'to_strike': -0.4,
                'date': date(2018, 4, 9),
                'expiration': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)
        option_contracts = option_chain.contracts
        short_contract = option_contracts[int(len(option_contracts) / 2)]
        long_lower_leg = Utils.create_option_leg_with_option_contract(
            option_contract=option_contracts[0],
            direction='LONG',
            quantity=1)
        short_leg = Utils.create_option_leg_with_option_contract(
            option_contract=short_contract,
            direction='SHORT',
            quantity=2)
        long_upper_leg = Utils.create_option_leg_with_option_contract(
            option_contract=option_contracts[-1],
            direction='LONG',
            quantity=1)
        butterfly = Butterfly(
            symbol='SPX',
            direction='LONG',
            quantity=10,
            opening_date=opening_date,
            first_leg=long_lower_leg,
            mid_leg=short_leg,
            third_leg=long_upper_leg)
        position = Position(trades=[butterfly])
        return position