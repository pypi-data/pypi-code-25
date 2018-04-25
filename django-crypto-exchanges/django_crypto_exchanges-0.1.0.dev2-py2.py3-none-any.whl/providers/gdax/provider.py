# Django libraries here
from django.conf import settings
from ..base import Provider
import datetime
from decimal import Decimal as D
import gdax
import itertools


class GdaxProvider(Provider):

    id = 'gdax'
    name = 'GDAX'

    def initialize_auth_client(self, *args, **kwargs):
        """
        Initialize authorized client for API calls.

        :param sandbox: boolean, if true then use sandbox mode for API
        :return: auth_client object
        """
        super().initialize_auth_client(*args, **kwargs)

        if kwargs.get("sandbox", False):
            return gdax.AuthenticatedClient(
                settings.GDAX_SANDBOX_API_KEY,
                settings.GDAX_SANDBOX_API_SECRET,
                settings.GDAX_SANDBOX_PASSPHRASE,
                api_url="https://api-public.sandbox.gdax.com"
            )

        return gdax.AuthenticatedClient(
            settings.GDAX_API_KEY,
            settings.GDAX_API_SECRET,
            settings.GDAX_PASSPHRASE
        )

    def initialize_public_client(self, *args, **kwargs):
        """
        Initialize public client for API calls.

        :param sandbox: boolean, if true then use sandbox mode for API
        :return: public_client object
        """
        super().initialize_public_client(*args, **kwargs)

        if kwargs.get("sandbox", False):
            return gdax.PublicClient(api_url="https://api-public.sandbox.gdax.com")

        return gdax.PublicClient()

    def get_currencies(self, *args, **kwargs):
        """

        :return:
        """
        client = self.initialize_public_client(sandbox=kwargs.get("sandbox", False))
        currencies = client.get_currencies()

        return [{
            "ticker_symbol": curr['id'],
            "name": curr['name'],
            "accuracy": len(curr['min_size'].split('.')[1].split('1')[0]) + 1
        } for curr in currencies]

    def get_products(self, *args, **kwargs):
        """

        :return:
        """
        client = self.initialize_public_client(sandbox=kwargs.get("sandbox", False))
        products = client.get_products()

        return [{
            "name": prod['id'],
            "base_currency": prod['base_currency'],
            "quote_currency": prod['quote_currency'],
            "base_min_size": prod['base_min_size'],
            "base_max_size": prod['base_max_size'],
            "quote_increment": prod['quote_increment']
        } for prod in products]

    def get_historic_rates(self, product, granularity, *args, **kwargs):
        """
        Get historic rates for a desired product with specified granularity and optional start/end dates.

        :param product: string containing the name of the product
        :param granularity: integer value for the number of seconds in granularity
        :param start: optional param for start date in ISO 8601 format str
        :param end: optional param for end date in ISO 8601 format str
        :return:
        """
        super().get_historic_rates(product, granularity, *args, **kwargs)

        client = self.initialize_public_client(sandbox=kwargs.get("sandbox", False))
        if 'start' not in kwargs and 'end' not in kwargs:
            historic_rates = client.get_product_historic_rates(product, granularity=granularity)
        else:
            historic_rates = client.get_product_historic_rates(
                product, start=kwargs['start'], end=kwargs['end'], granularity=granularity
            )

        return [{
            "datetime": datetime.datetime.fromtimestamp(hr[0], datetime.timezone.utc),
            "low": hr[1],
            "high": hr[2],
            "open": hr[3],
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

        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        order_book = client.get_product_order_book(product, level)

        # fix order book
        order_book['last_update_id'] = order_book.pop('sequence')
        order_book['asks'] = self._fix_order_book_sublist(order_book.pop('asks'))
        order_book['bids'] = self._fix_order_book_sublist(order_book.pop('bids'))

        return order_book

    def get_accounts(self, *args, **kwargs):
        """

        :param sandbox: boolean, if true then use sandbox mode for API
        :return:
        """
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        accounts = client.get_accounts()

        return [{
            "currency": account["currency"],
            "balance": account["balance"],
            "available": account["available"],
            "hold": account["hold"]
        } for account in accounts]

    def get_available_account_balance(self, currency, *args, **kwargs):
        """
        Get account balance for desired currency.

        :param currency: the ticker_symbol for the desired currency (e.g. BTC, USD)
        :param sandbox: boolean, if true then use sandbox mode for API
        :return:
        """
        super().get_available_account_balance(currency, *args, **kwargs)

        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))

        try:
            return D(next(acct for acct in client.get_accounts() if acct['currency'] == currency)['available'])
        except IndexError:
            raise ValueError("Currency entered is not available.")

    @staticmethod
    def _return_formatted_order(order):
        return {
            "product": order["product_id"],
            "order_id": order["id"],
            "price": order["price"],
            "size": order["size"],
            "time_in_force": order["time_in_force"],
            "type": order["type"],
            "side": order["side"],
            "post_only": order["post_only"],
            "status": order["status"],
            "created_at": datetime.datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "fill_fees": order["fill_fees"],
            "filled_size": order["filled_size"],
            "settled": order["settled"]
        }

    def get_open_orders(self, product, *args, **kwargs):
        """
        Get orders for :product: that are currently open

        :param product:
        :param sandbox:
        :return:
        """
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        open_orders = list(itertools.chain.from_iterable(client.get_orders()))

        return [self._return_formatted_order(order) for order in open_orders if order.get("product_id") == product]

    def get_order(self, product, order_id, *args, **kwargs):
        """

        :param product:
        :param order_id:
        :return:
        """
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        order = client.get_order(order_id)

        return self._return_formatted_order(order)

    def buy(self, product, price, size, order_type, *args, **kwargs):
        """
        Create a buy order for a product

        :param product: the product to be transacted
        :param price: the desired price of the product
        :param size: how much of the product to place in the order
        :param order_type: type of order, e.g. limit, stop_loss, etc.
        :return: an order dict
        """
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        order = client.buy(
            product_id=product,
            price=price,
            size=size,
            type=order_type,
            post_only=kwargs.get('post_only', False)
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
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        order = client.sell(
            product_id=product,
            price=price,
            size=size,
            type=order_type,
            post_only=kwargs.get('post_only', False)
        )

        return self._return_formatted_order(order)

    def cancel(self, product, order_id, *args, **kwargs):
        """
        Cancel an order with order id :order_id:

        :param product:
        :param order_id:
        :param sandbox: boolean, if true then use sandbox mode for API
        :return: order_id for the order that was canceled
        """
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        return client.cancel_order(order_id)

    def cancel_all(self, product, *args, **kwargs):
        """
        Cancel all open orders for the :product:

        :param product: Product object instance
        :param sandbox: boolean, if true then use sandbox mode for API
        :return: list of order ids for canceled orders
        """
        client = self.initialize_auth_client(sandbox=kwargs.get("sandbox", False))
        return client.cancel_all(product=product)


providers = [GdaxProvider]
