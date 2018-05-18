from django.db import models
from django.conf import settings

from money import Money, Currency

from .mixins import MoneyObjectsManager


class Rate(models.Model):
    CURRENCY_CHOICES = ((c.code, c.name) for c in settings.CURRENCIES)

    currency = models.CharField(_('Currency'), max_length=8, choices=CURRENCY_CHOICES)
    related_currency = models.CharField(_('Related currency'), max_length=8, choices=CURRENCY_CHOICES)
    value = models.FloatField()

    def __str__(self):
        return f"{self.currency} to {self.related_currency}"


class MoneyModel(models.Model):
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=8, choices=Rate.CURRENCY_CHOICES)

    @property
    def money(self):
        return Money.int_to_money(self.amount, Currency.get(self.currency))

    @money.setter
    def money(self, value):
        if isinstance(value, Money) and value.currency.code == self.currency:
            self.amount = int(value)
            self.save()
        else:
            raise TypeError("Must be Money instance with existed Currency")

    def __str__(self):
        return f'{self.money}'


class MoneyMixin(object):
    __money_fields = []

    objects = MoneyObjectsManager()

    def __init__(self, *args, **kwargs):
        self.__money_fields = [field for field in self._meta.fields if isinstance(field, MoneyField)]
        for field in self.__money_fields:
            money = kwargs.get(field.name)
            if money:
                money_instance = MoneyModel.objects.create(amount=int(money), currency=money.currency.code)
                kwargs.update({field.name: money_instance})
        super().__init__(*args, **kwargs)

    @classmethod
    def get_money_field_names(cls):
        return [field.name for field in cls._meta.fields if isinstance(field, MoneyField)]
