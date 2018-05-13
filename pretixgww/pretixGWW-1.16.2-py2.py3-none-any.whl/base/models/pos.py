import sys
import uuid
from datetime import date, datetime, time
from decimal import Decimal, DecimalException
from typing import Tuple

import dateutil.parser
import pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Func, Q, Sum
from django.utils import formats
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.timezone import is_naive, make_aware, now
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from i18nfield.fields import I18nCharField, I18nTextField
from pretix.base.models import User,Event

class Opening_closing_balance(models.Model ):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='OCB',
    )
    date = models.DateField(auto_now=False, auto_now_add=False, blank=True)
    shift_starting_time = models.TimeField(auto_now=False, auto_now_add=False, blank=True)
    cashier_name=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_name',
    )
    opening_balance = models.FloatField(default=0)
    opening_balance = models.FloatField(default=0)
    total_sales = models.FloatField(default=0)
    total_closing_cost = models.FloatField(default=0)
    opening_balance = models.FloatField(default=0)
    shift_ending_time = models.TimeField(auto_now=False, auto_now_add=False, blank=True)

