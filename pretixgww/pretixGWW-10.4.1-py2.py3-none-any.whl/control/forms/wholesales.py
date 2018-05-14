from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

from pretix.base.forms import I18nModelForm, PlaceholderValidator
from pretix.base.models import (
    InvoiceAddress, Item, ItemAddOn, Order, OrderPosition,
)
from pretix.base.models.event import SubEvent
from pretix.base.models.wholesale import WholesaleAccount
from pretix.base.services.pricing import get_price
from pretix.control.forms.widgets import Select2
from pretix.helpers.money import change_decimal_field


class WholesaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['class'] = 'phone'
        self.fields['zip_code'].widget.attrs['class'] = 'zip_code'

    class Meta:
        model = WholesaleAccount
        exclude = ['event']

    def save(self, commit=True):
        wholesale = super(WholesaleForm, self).save(commit=False)
        wholesale.event = self.event
        wholesale.save()