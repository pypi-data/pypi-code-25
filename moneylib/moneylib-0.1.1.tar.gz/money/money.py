from .exceptions import CurrenciesNotSpecifiedError, CurrencyDoesNotExist, MultipleCurrenciesFound

CURRENCIES = []

def update_currencies(currencies):
    if not hasattr(currencies, '__iter__'):
        raise TypeError
    CURRENCIES.extend(currencies)


class Currency(object):
    def __init__(self, name, code, decimal_places, prefix="", suffix=""):
        self.name = name
        self.code = code
        self.decimal_places = decimal_places
        self.prefix = prefix
        self.suffix = suffix

    @property
    def factor(self):
        return 10 ** self.decimal_places

    @staticmethod
    def get(code):
        try:
            if CURRENCIES:
                currencies = filter(lambda x: x.code == code, CURRENCIES)
                if not currencies:
                    raise CurrencyDoesNotExist(code)
                if len(currencies) > 1:
                    raise MultipleCurrenciesFound(code)
                return currencies[0]
            return None
        except AttributeError:
            raise CurrenciesNotSpecifiedError
        except NameError:
            raise CurrenciesNotSpecifiedError


class Money(object):
    """
    Money type is for the convenient work with moneylib.
    """
    __amount = 0
    currency = None
    _pk = None

    def __init__(self, amount, currency, pk=None):  # takes a normalized amount and save it as integer
        if not isinstance(currency, Currency):
            raise TypeError
        self.__amount = int(float(amount) * currency.factor)
        self.currency = currency
        self._pk = pk

    def __str__(self):
        return "{}{}{}".format(self.currency.prefix, self.amount, self.currency.suffix)

    def __int__(self):
        return self.__amount

    def __float__(self):
        return float(int(self) / self.currency.factor)

    def __abs__(self):
        res = abs(int(self)) / self.currency.factor
        return Money(res, self.currency)

    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        if not self.currency is other.currency:
            raise TypeError
        return int(self) == int(other)

    def __ne__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        return int(self) != int(other)

    def __lt__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        return int(self) < int(other)

    def __le__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        return int(self) <= int(other)

    def __gt__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        return int(self) > int(other)

    def __ge__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        return int(self) >= int(other)

    def __add__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        res = (int(self) + int(other)) / self.currency.factor
        return Money(res, self.currency)

    def __sub__(self, other):
        if not self.currency is other.currency:
            raise TypeError
        res = (int(self) - int(other)) / self.currency.factor
        return Money(res, self.currency)

    def __mul__(self, other):
        if not isinstance(other, float) and not isinstance(other, int):
            raise TypeError
        res = (int(self) * other) / self.currency.factor
        return Money(res, self.currency)

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            res = (int(self) / other) / self.currency.factor
            return Money(res, self.currency)
        if isinstance(other, Money):
            return int(self) / int(other)
        raise TypeError

    def __floordiv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            res = (float(self) // other)
            return Money(res, self.currency)
        if isinstance(other, Money):
            return float(self) // float(other)
        raise TypeError

    def __mod__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            res = (float(self) % other)
            return Money(res, self.currency)
        if isinstance(other, Money):
            return float(self) % float(other)
        raise TypeError

    @property
    def amount(self):
        return self.__amount / self.currency.factor

    @amount.setter
    def amount(self, value):
        self.__amount = value * self.currency.factor

    # def to_currency(self, related_currency):  # returns new Money object
    #     if related_currency == self.currency:
    #         return self
    #     rate = self.currency.rate_to(related_currency)
    #     return Money(self.amount * rate, related_currency)

    @staticmethod
    def int_to_money(amount, currency):
        return Money(amount / currency.factor, currency)
