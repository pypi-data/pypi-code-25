import math


class ProviderException(Exception):
    pass


class Provider(object):

    def rounddown(self, number, decimal_places=0):
        """
        Round down the entered `number` to the desired decimal places.

        :param number: A float value (e.g. 100.2536874)
        :param decimal_places: An integer value (e.g. 3)
        :return: A float value (e.g. 100.253)
        """
        # Start param error prevention
        if type(number) is not float:
            raise TypeError("number must be a float.")

        if type(decimal_places) is not int:
            raise TypeError("decimal_places must be an int.")
        # End param error prevention

        factor = 10 ** decimal_places
        return math.floor(number * factor) / factor

    def initialize_auth_client(self, *args, **kwargs):
        raise NotImplementedError

    def initialize_public_client(self, *args, **kwargs):
        raise NotImplementedError

    def get_accounts(self):
        raise NotImplementedError

    def get_available_account_balance(self, *args, **kwargs):
        raise NotImplementedError

    def get_currencies(self, *args, **kwargs):
        raise NotImplementedError

    def get_products(self, *args, **kwargs):
        raise NotImplementedError
