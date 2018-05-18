class CurrenciesNotSpecifiedError(Exception):
    def __str__(self):
        return 'CURRENCIES must be specified'


class CurrencyDoesNotExist(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Currency with code "%s" does not exist' % self.code


class MultipleCurrenciesFound(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Multiple currencies found for code "%s"' % self.code
