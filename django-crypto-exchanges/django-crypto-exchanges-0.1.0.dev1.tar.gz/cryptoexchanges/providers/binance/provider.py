# Django libraries here
from django.conf import settings
from ..base import Provider
import datetime
import binance


class BinanceProvider(Provider):

    id = 'binance'
    name = 'Binance'

    def initialize_auth_client(self, *args, **kwargs):
        """
        Initialize authorized client for API calls.

        :return: client object
        """
        pass

    def initialize_public_client(self, *args, **kwargs):
        """
        Initialize authorized client for API calls.

        :return: client object
        """
        pass

    def get_accounts(self, *args, **kwargs):
        """

        :return:
        """
        pass

    def get_available_account_balance(self, currency, *args, **kwargs):
        """

        :return:
        """
        pass

    def get_currencies(self, *args, **kwargs):
        """

        :return:
        """
        pass

    def get_products(self, *args, **kwargs):
        """

        :return:
        """
        pass

    def get_historic_rates(self, product, *args, **kwargs):
        """

        :return:
        """
        pass


providers = [BinanceProvider]
