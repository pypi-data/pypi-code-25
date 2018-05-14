from django.db import models

from pretix.base.models import  Event
from .base import LoggedModel
from django.conf import settings


class WholesaleAccount(LoggedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="wholesales")
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    tax = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=255, blank=True)

class WholesaleAccounts(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="wholesales_event")
    company_name =models.CharField(max_length=255)
    contact_fname =models.CharField(max_length=255)
    contact_lname =models.CharField(max_length=255)
    street_address=models.CharField(max_length=255)
    zipcode =models.CharField(max_length=20,    blank=True, null=True)
    city =models.CharField(max_length=100,default=None,blank=True, null=True)
    country =models.CharField(max_length=100,default=None,blank=True, null=True)
    state = models.CharField(max_length=255, blank=True)
    email=models.EmailField(unique=True, db_index=True, null=False, blank=False,
                              verbose_name=('E-mail'))
    phone=models.CharField(max_length=255)
    tax_id=models.CharField(max_length=255)
    account_type=models.CharField(max_length=50,
                              choices=settings.ACCOUNT_TYPE,
                              verbose_name=('Account Type'))

