# Django libraries here
from django.conf import settings
from ..base import Provider
import datetime
from decimal import Decimal as D
from binance.client import Client
from binance.exceptions import BinanceRequestException, BinanceAPIException


class BinanceProvider(Provider):

    id = 'binance'
    name = 'Binance'

    def initialize_auth_client(self, *args, **kwargs):
        """
        Initialize authorized client for API calls.

        :return: client object
        """
        super().initialize_public_client(*args, **kwargs)
        return Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)

    def initialize_public_client(self, *args, **kwargs):
        """
        Initialize public client for API calls.

        :return: client object
        """
        super().initialize_public_client(*args, **kwargs)
        print("Note: There's no distinct public client for Binance.")
        return self.initialize_auth_client(*args, **kwargs)

    def get_currencies(self, *args, **kwargs):
        """

        :return:
        """
        client = self.initialize_auth_client()
        symbols = client.get_exchange_info()['symbols']

        currencies = []
        for currency in symbols:
            # add quote currency
            currencies.append({
                'ticker_symbol': currency['quoteAsset'],
                'name': currency['quoteAsset'],
                'accuracy': currency['quotePrecision']
            })

            # add base currency
            currencies.append({
                'ticker_symbol': currency['baseAsset'],
                'name': currency['baseAsset'],
                'accuracy': currency['baseAssetPrecision']
            })

        return [dict(tupleized) for tupleized in set(tuple(item.items()) for item in currencies)]

    def get_products(self, *args, **kwargs):
        """

        :return:
        """
        client = self.initialize_auth_client()
        symbols = client.get_exchange_info()['symbols']

        return [{
            "name": prod['symbol'],
            "base_currency": prod['baseAsset'],
            "quote_currency": prod['quoteAsset'],
            "base_min_size": prod['filters'][0]['minPrice'],
            "base_max_size": prod['filters'][0]['maxPrice'],
            "quote_increment": prod['filters'][1]['stepSize']
        } for prod in symbols if prod['status'] == 'TRADING']

    def get_historic_rates(self, product, granularity, *args, **kwargs):
        """

        :return:
        """
        super().get_historic_rates(product, granularity, *args, **kwargs)

        granularity_map = {
            60: {"start_str": "350 mins ago", "interval": "1m"},
            300: {"start_str": "1750 mins ago", "interval": "5m"},
            900: {"start_str": "5250 mins ago", "interval": "15m"},
            3600: {"start_str": "350 hours ago", "interval": "1h"},
            21600: {"start_str": "2100 hours ago", "interval": "6h"},
            86400: {"start_str": "350 days ago", "interval": "1d"},
        }

        client = self.initialize_auth_client()
        if 'start' not in kwargs and 'end' not in kwargs:
            historic_rates = client.get_historical_klines(
                product,
                start_str=granularity_map[granularity]['start_str'],
                interval=granularity_map[granularity]['interval']
            )
        else:
            historic_rates = client.get_historical_klines(
                product,
                start_str=kwargs['start'],
                end_str=kwargs['end'],
                interval=granularity_map[granularity]['interval']
            )

        return [{
            "datetime": datetime.datetime.fromtimestamp(hr[0] / 1000, datetime.timezone.utc),
            "low": hr[3],
            "high": hr[2],
            "open": hr[1],
            "close": hr[4],
            "volume": hr[5]
        } for hr in historic_rates]

    def get_order_book(self, product, level, *args, **kwargs):
        """
        Get the order book for a given product

        :param product: trading pair
        :param level: must be 1 or 2.
            if 1, return only best bid/ask pair
            if 2, return top 50 bids and asks
        :return: return an order book dict containing 3 keys: bids, asks, last_update_id
        """
        super().get_order_book(product, level, *args, **kwargs)

        client = self.initialize_auth_client()

        order_book = client.get_order_book(symbol=product)
        order_book['last_update_id'] = order_book.pop('lastUpdateId')

        # Only the best bid and ask
        if level == 1:
            order_book['asks'] = self._fix_order_book_sublist([order_book['asks'][-1]])
            order_book['bids'] = self._fix_order_book_sublist([order_book['bids'][0]])

        # Top 50 bids and asks (aggregated)
        elif level == 2:
            order_book['asks'] = self._fix_order_book_sublist(order_book['asks'][-50:-1])
            order_book['bids'] = self._fix_order_book_sublist(order_book['bids'][0:50])

        return order_book

    def get_accounts(self, *args, **kwargs):
        """

        :return:
        """
        client = self.initialize_auth_client()
        account = client.get_account()

        return [{
            "currency": acct["asset"],
            "balance": float(acct["free"]) + float(acct["locked"]),
            "available": acct["free"],
            "hold": acct["locked"],
        } for acct in account['balances']]

    def get_available_account_balance(self, currency, *args, **kwargs):
        """

        :return:
        """
        super().get_available_account_balance(currency, *args, **kwargs)

        client = self.initialize_auth_client()

        try:
            return D(client.get_asset_balance(currency)['free'])
        except IndexError:
            raise ValueError("Currency entered is not available.")

    @staticmethod
    def _return_formatted_order(order, commission_rate):
        return {
            "product": order["symbol"],
            "order_id": order["orderId"],
            "price": order["price"],
            "size": order["origQty"],
            "time_in_force": order["timeInForce"],
            "type": order["type"],
            "side": order["side"],
            "post_only": False,
            "status": order["status"],
            "created_at": datetime.datetime.fromtimestamp(order["time"] / 1000, datetime.timezone.utc),
            "fill_fees": order["executedQty"] * commission_rate,
            "filled_size": order["executedQty"],
            "settled": order["origQty"] == order["executedQty"]
        }

    def _get_commission_rate(self, maker):
        client = self.initialize_auth_client()
        account = client.get_account()
        return account["makerCommission"] / 10000 if maker else account["takerCommission"] / 10000

    def get_open_orders(self, product, maker=False, *args, **kwargs):
        """
        Get orders for :product: that are currently open

        :param product:
        :param maker:
        :return:
        """
        client = self.initialize_auth_client()
        open_orders = client.get_open_orders(symbol=product)

        # get effective commission rate
        commission_rate = self._get_commission_rate(maker)

        return [self._return_formatted_order(order, commission_rate) for order in open_orders]

    def get_order(self, product, order_id, maker=False, *args, **kwargs):
        """

        :param product:
        :param order_id:
        :param maker:
        :return:
        """
        client = self.initialize_auth_client()
        order = client.get_order(symbol=product, orderId=order_id)

        return self._return_formatted_order(order, self._get_commission_rate(maker))

    def buy(self, product, price, size, order_type, *args, **kwargs):
        """
        Create a buy order for a product

        :param product: the product to be transacted
        :param price: the desired price of the product
        :param size: how much of the product to place in the order
        :param order_type: type of order, e.g. limit, stop_loss, etc.
        :return: an order dict
        """
        client = self.initialize_auth_client()
        order = client.create_order(
            symbol=product,
            side="buy",
            price=price,
            quantity=size,
            type=order_type,
            timeInForce=kwargs.get("time_in_force", "GTC")
        )

        return self._return_formatted_order(order)

    def sell(self, product, price, size, order_type, *args, **kwargs):
        """
        Create a sell order for a product

        :param product: the product to be transacted
        :param price: the desired price of the product
        :param size: how much of the product to place in the order
        :param order_type: type of order, e.g. limit, stop_loss, etc.
        :return: an order dict
        """
        client = self.initialize_auth_client()
        order = client.create_order(
            symbol=product,
            side="sell",
            price=price,
            quantity=size,
            type=order_type,
            timeInForce=kwargs.get("time_in_force", "GTC")
        )

        return self._return_formatted_order(order)

    def cancel(self, product, order_id, *args, **kwargs):
        """
        Cancel an order with order id :order_id:

        :param product:
        :param order_id:
        :return: order_id for the order that was canceled
        """
        client = self.initialize_auth_client()
        return client.cancel_order(symbol=product, orderId=order_id)['orderId']

    def cancel_all(self, product, *args, **kwargs):
        """
        Cancel all open orders for the :product:

        :param product: Product object instance
        :return: list of order ids for canceled orders
        """
        open_orders = self.get_open_orders(symbol=product)

        responses = []
        for order in open_orders:
            try:
                responses.append(self.cancel(product, order['orderId']))
            except BinanceRequestException as e:
                print(e)
            except BinanceAPIException as e:
                print(e)

        return responses


providers = [BinanceProvider]
