# -*- coding: utf-8 -*-
from django.conf import settings as dj_settings
from appconf import AppConf
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _

settings = dj_settings

class PayApiAppConf(AppConf):

    PAY_API_ORDER_MODEL = 'module.Model'
    PAY_API_PAYMENT_MODEL = None
    PAY_API_TESTING = True
    PAY_API_NOTIFY_URL = None
    PAY_API_CLIENT_SECRET = None
    PAY_API_POS_ID = None
    PAY_API_SECOND_KEY = None

    CURRENCY = 'PLN'

    if hasattr(settings, 'PAY_API_TESTING'):
        TESTING = settings.PAY_API_TESTING
    else:
        TESTING = False

    if TESTING:
        NOTIFY_URL = 'http://snd.integree.eu/notify'
        AUTH_URL = 'https://secure.snd.payu.com/pl/standard/user/oauth/authorize'
        ORDER_URL = 'https://secure.snd.payu.com/api/v2_1/orders/'
        DELETE_TOKEN_URL = 'https://secure.snd.payu.com/api/v2_1/tokens/'
        PAYMETHODS_URL = 'https://secure.snd.payu.com/api/v2_1/paymethods/'
    else:
        NOTIFY_URL = 'http://snd.integree.eu/notify'
        AUTH_URL = 'https://secure.payu.com/pl/standard/user/oauth/authorize'
        ORDER_URL = 'https://secure.payu.com/api/v2_1/orders/'
        DELETE_TOKEN_URL = 'https://secure.payu.com/api/v2_1/tokens/'
        PAYMETHODS_URL = 'https://secure.payu.com/api/v2_1/paymethods/'

    PAYMENT_MODEL = None

    PLN = 'PLN'
    EUR = 'EUR'
    USD = 'USD'
    CZK = 'CZK'
    GBP = 'GBP'

    CURRENCY_CHOICE = (
        (PLN, u"Złoty"),
        (EUR, u"Euro"),
        (USD, u"Dolar amerykański"),
        (CZK, u"Korona czeska"),
        (GBP, u"Funt brytyjski"),
    )

    CURRENCY_DATA = {
        PLN: {
          'name': u"Złoty",
          'sub_unit': Decimal(100),
        },
        EUR: {
          'name': u"Euro",
          'sub_unit': Decimal(100),
        },
        USD: {
          'name': u"Dolar amerykański",
          'sub_unit': Decimal(100),
        },
        CZK: {
          'name': u"Korona czeska",
          'sub_unit': Decimal(100),
        },
        GBP: {
          'name': u"Funt brytyjski",
          'sub_unit': Decimal(100),
        },
    }
