from money import (
    Currency as MoneylibCurrency,
    Money as MoneylibMoney,
)

from .models import Rate


class Currency(MoneylibCurrency):
    def rate_to(self, related_currency):
        return Rate.objects.get(currency=self.code, related_currency=related_currency.code).value

    def back_rate_to(self, related_currency):
        return 1 / Rate.objects.get(currency=self.code, related_currency=related_currency.code).value

    def bid(self, related_currency):
        """It is an alias for the rate_to method"""
        return self.rate_to(related_currency)

    def ask(self, related_currency):
        """It is an alias for the back_rate_to method"""
        return self.back_rate_to(related_currency)


class Money(MoneylibMoney):
    def to_currency(self, related_currency):  # returns new Money object
        if related_currency == self.currency:
            return self
        rate = self.currency.rate_to(related_currency)
        return Money(self.amount * rate, related_currency)
