# Django libraries here
from django.conf import settings
from ..base import Provider
import datetime
import gdax


class GdaxProvider(Provider):

    id = 'gdax'
    name = 'GDAX'

    def initialize_auth_client(self, sandbox=False):
        """
        Initialize authorized client for API calls.

        :param sandbox: boolean, if true then use sandbox mode for API
        :return: auth_client object
        """
        # Start param error prevention
        if type(sandbox) is not bool:
            raise TypeError("sandbox must be a bool.")
        # End param error prevention

        if sandbox:
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

    def initialize_public_client(self, sandbox=False):
        """
        Initialize public client for API calls.

        :param sandbox: boolean, if true then use sandbox mode for API
        :return: public_client object
        """
        # Start param error prevention
        if type(sandbox) is not bool:
            raise TypeError("sandbox must be a bool.")
        # End param error prevention

        if sandbox:
            return gdax.PublicClient(api_url="https://api-public.sandbox.gdax.com")

        return gdax.PublicClient()

    def get_accounts(self, sandbox=False):
        pass

    def get_available_account_balance(self, currency, sandbox=False):
        """
        Get account balance for desired currency.

        :param currency: the ticker_symbol for the desired currency (e.g. BTC, USD)
        :param sandbox: if True, use sandbox mode for API
        :return:
        """
        # Start param error prevention
        if type(currency) is not str:
            raise TypeError("currency must be a str.")

        if type(sandbox) is not bool:
            raise TypeError("sandbox must be a bool.")
        # End param error prevention

        auth_client = self.initialize_auth_client(sandbox)

        try:
            return D(next(acct for acct in auth_client.get_accounts() if acct['currency'] == currency)['available'])
        except IndexError:
            raise ValueError("Currency entered is not available.")

    def get_currencies(self, sandbox=False):
        """

        :return:
        """
        client = self.initialize_public_client(sandbox)
        currencies = client.get_currencies()

        # IF DIFFERENT THAN 0.01, define minimum purchase/sale sizes for each currency
        min_sizes = {
            'LTC': 0.1
        }

        return [{
            "ticker_symbol": curr['id'],
            "name": curr['name'],
            "min_size": min_sizes.get(curr['id'], 0.01),
            "accuracy": len(curr['min_size'].split('.')[1].split('1')[0]) + 1,
            "active": True,
        } for curr in currencies]

    def get_products(self, sandbox=False):
        """

        :return:
        """
        client = self.initialize_public_client(sandbox)
        products = client.get_products()

        return [{
            "name": prod['id'],
            "base_currency": prod['base_currency'],
            "quote_currency": prod['quote_currency'],
            "base_min_size": prod['base_min_size'],
            "base_max_size": prod['base_max_size'],
            "quote_increment": prod['quote_increment'],
            "active": True
        } for prod in products]

    def get_historic_rates(self, product, granularity, **kwargs):
        """
        Get historic rates for a desired product with specified granularity and optional start/end dates.

        :param product: string containing the name of the product
        :param granularity: integer value for the number of seconds in granularity
        :param start: optional param for start date in ISO 8601 format str
        :param end: optional param for end date in ISO 8601 format str
        :return:
        """
        # check granularity is valid
        if granularity not in [60, 300, 900, 3600, 21600, 86400]:
            raise ValueError("Granularity must be one of 60, 300, 900, 3600, 21600, 86400.")

        client = self.initialize_public_client()
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


providers = [GdaxProvider]
