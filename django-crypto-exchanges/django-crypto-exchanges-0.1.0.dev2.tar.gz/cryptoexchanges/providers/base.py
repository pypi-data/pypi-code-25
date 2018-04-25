class ProviderException(Exception):
    pass


class Provider(object):

    # internal methods
    @staticmethod
    def _check_sandbox_bool(sandbox):
        # Start param error prevention
        if type(sandbox) is not bool:
            raise TypeError("sandbox must be a bool.")
        # End param error prevention

    @staticmethod
    def _fix_order_book_sublist(order_book_sublist):
        return [
            [
                float(item[0]),  # price
                float(item[1])   # size
            ]
            for item in order_book_sublist
        ]

    # client methods
    def initialize_auth_client(self, *args, **kwargs):
        # Start param error prevention
        self._check_sandbox_bool(sandbox=kwargs.get("sandbox", False))
        # End param error prevention

    def initialize_public_client(self, *args, **kwargs):
        # Start param error prevention
        self._check_sandbox_bool(sandbox=kwargs.get("sandbox", False))
        # End param error prevention

    # information methods
    def get_currencies(self, *args, **kwargs):
        raise NotImplementedError

    def get_products(self, *args, **kwargs):
        raise NotImplementedError

    def get_historic_rates(self, product, granularity, *args, **kwargs):
        # Start param error prevention
        if granularity not in [60, 300, 900, 3600, 21600, 86400]:
            raise ValueError("Granularity must be one of 60, 300, 900, 3600, 21600, 86400.")
        # End param error prevention

    def get_order_book(self, product, level, *args, **kwargs):
        # Start param error prevention
        self._check_sandbox_bool(sandbox=kwargs.get("sandbox", False))

        if type(level) is not int:
            raise TypeError("level must be an int.")

        if level not in [1, 2]:
            raise ValueError("level must 1 or 2.")
        # End param error prevention

    # authenticated information methods
    def get_accounts(self):
        raise NotImplementedError

    def get_available_account_balance(self, currency, *args, **kwargs):
        # Start param error prevention
        self._check_sandbox_bool(sandbox=kwargs.get("sandbox", False))

        if type(currency) is not str:
            raise TypeError("currency must be a str.")
        # End param error prevention

    def get_open_orders(self, *args, **kwargs):
        raise NotImplementedError

    def get_order(self, *args, **kwargs):
        raise NotImplementedError

    # authenticated action methods
    def buy(self, *args, **kwargs):
        raise NotImplementedError

    def sell(self, *args, **kwargs):
        raise NotImplementedError

    def cancel(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all(self, *args, **kwargs):
        raise NotImplementedError
