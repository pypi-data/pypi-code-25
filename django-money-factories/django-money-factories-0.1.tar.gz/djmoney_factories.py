import factory
from factory import fuzzy


class ExchangeBackendFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'exchange.ExchangeBackend'

    name = factory.Faker('user_name')
    base_currency = factory.Faker('currency_code')


class RateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'exchange.Rate'

    currency = factory.Faker('currency_code')
    value = fuzzy.FuzzyFloat(0, 1)
    backend = factory.SubFactory(ExchangeBackendFactory)
