from django.db import models

from money import Money, Currency

from .models import MoneyModel


class MoneyField(models.OneToOneField):
    def __init__(self, *args, **kwargs):
        kwargs['to'] = 'money.MoneyModel'
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "MoneyField"

    @staticmethod
    def parse_value(value):
        return Money.int_to_money(value.amount, Currency.get(value.currency))

    def from_db_value(self, value, expression, connection, *args, **kwargs):
        if value is None:
            return value
        if isinstance(value, int):
            return value
        raise TypeError

    def to_python(self, value):
        if isinstance(value, Money) or value is None:
            return value
        return self.parse_value(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return value
        return MoneyModel.objects.create(amount=int(value), currency=value.currency.code)
