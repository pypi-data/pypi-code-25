# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from decimal import Decimal
from django.http.response import Http404, HttpResponse
from django.utils import timezone
from django.views.generic.base import View
from pay_api import PayApiError, get_payment_model, get_config_model
from pay_api.classes import OrderItem
from pay_api.conf import settings
import ast
import hashlib
import json
import logging
import requests
import paypalrestsdk
from paypalrestsdk.notifications import WebhookEvent

def post(request, *args, **kwargs):

    data = json.loads(request.body)

    event_body = request.body
    transmission_id = request.META['HTTP_PAYPAL_TRANSMISSION_ID']
    timestamp = request.META['HTTP_PAYPAL_TRANSMISSION_TIME']
#    webhook_id = settings.PAY_API_PAYPAL_WEBHOOK_ID
    actual_signature = request.META['HTTP_PAYPAL_TRANSMISSION_SIG']
    cert_url = request.META['HTTP_PAYPAL_CERT_URL']
    auth_algo = request.META['HTTP_PAYPAL_AUTH_ALGO']
    
    
    order_id = data['resource']['id']
    payment_id = data['resource']['parent_payment']
    try:
        payment = get_payment_model().objects.get(ext_order_id = payment_id)
    except get_payment_model().DoesNotExist:
        return HttpResponse("ok", status = 200)

    config = PayBackendConfig.get_config_by_backend(payment.backend)

    response = WebhookEvent.verify(transmission_id, timestamp, config.webhook_id, event_body, cert_url, actual_signature, auth_algo)
    if response:
        
        if data['event_type'] == 'PAYMENT.SALE.COMPLETED':
            amount_paid = data['resource']['amount']['total']
            payment.ext_order_id = order_id
            payment.amount_paid = amount_paid
            payment.save()
            payment.change_status(get_payment_model().COMPLETED)
            
        elif data['event_type'] == 'PAYMENT.SALE.DENIED':
            payment.change_status(get_payment_model().REJECTED)
            
        elif data['event_type'] == 'PAYMENT.SALE.PENDING':
            payment.change_status(get_payment_model().PENDING)
            
        elif data['event_type'] == 'PAYMENT.SALE.REFUNDED':
            payment.change_status(get_payment_model().REFUNDED)
    
    return HttpResponse("ok", status = 200)

def get(request, *args, **kwargs):
    auth_data = {
        "mode": "sandbox", # sandbox or live
        "client_id": "AS3RJDVf-1yowanwVAcJoSw6oGd1MD4AHBasuUS4j0e9pZSSwf4NwRaMX_r0B0KMtcHQ1-_lIUegXBwk",
        "client_secret": "EOMOaDYiZlXPWv-IPGtGehpFg3Whu9KK3qTcAsPaKjBckWy_cApJTjT2E_DBSFkzDhPvClx-OLy2HBst"  
     }
    paypalrestsdk.configure(auth_data)
    
    paymentId = request.GET.get('paymentId', None)
    PayerID = request.GET.get('PayerID', None)
    token = request.GET.get('token', None)
    
    if paymentId and PayerID:
        payment = paypalrestsdk.Payment.find(paymentId)
        if payment.execute({"payer_id": "HEVJP549N7QXG"}):
            print 'true'
            request.GET['status'] = 'success'
        else:
            print 'false'
            request.GET['status'] = 'failure'
    else:
        print 'false'
        request.GET['status'] = 'failure'

def create_payment(order, ext_order_obj, description, backend_config, url = settings.PAY_API_DEFAULT_NOTIFY_URL, **kwargs):
    api = __get_api(backend_config)
    
    processor_data = {
      'order': order,
      'ext_order_obj': ext_order_obj,
      'description': description,
      'currency': order.currency,
      'return_url': kwargs.get('return_url'),
      'cancel_url': kwargs.get('cancel_url'),
      'backend_config': backend_config,
    }
    
    processor = PaymentProcessor(**processor_data)
    p = paypalrestsdk.Payment(processor.as_dict(), api = api)
    payment = processor.as_payment_obj()
    if p.create():
        for link in p.links:
            if link.rel == 'self':
                payment.ext_order_id = link.href.split('/')[-1]
                payment.save()
        return p.links
    else:
        raise PayApiError(payment.error)
    
def __get_api(backend_config):
    return paypalrestsdk.Api({
         'mode': 'sandbox' if settings.PAY_API_TESTING else 'live',
         'client_id': backend_config.shop_id,
         'client_secret': backend_config.send_key
    })

class PaymentProcessor(object):
    "Klasa która służy za pośrednika między API a modelem zamówienia głównego projektu."

    def __init__(self, **kwargs):
        self.order = kwargs.get('order')
        self.ext_order_obj = kwargs.get('ext_order_obj')
        self.currency = kwargs.get('currency', settings.PAY_API_CURRENCY)
        self.description = kwargs.get('description')
        self.return_url = kwargs.get('return_url')
        self.cancel_url = kwargs.get('cancel_url')
        self.order_items = self.order.order_items
        self.backend_config = kwargs.get('backend_config')

    def add_order_items(self, obj):
        "Dodaj pozycje zamówienia, przyjmuje instancje klasy OrderItem"
        if isinstance(obj, OrderItem):
            self.order_items.append(obj)
        elif isinstance(obj, type([])):
            self.order_items.extend(obj)
        else:
            raise PayApiError(u"Zły format order_item. Funkcja add_order_items przyjmuje obiekt OrderItem lub listę złożoną z instancji klasy OrderItem.")
        
    def as_dict(self):
        total = Decimal(0)
        items = []
        
        for i in self.order_items:
            total += Decimal(i.unit_price) * Decimal(i.quantity)
            
            item_dict = {
             'name': i.name,
             'sku': 1,
             'price': str(i.unit_price),
             'quantity': str(i.quantity),
             'currency': self.currency
            }
            
            items.append(item_dict)
    
        dict = {
            'intent': "sale",
            'payer': {"payment_method": "paypal"},
            'redirect_urls': {
                'return_url': self.return_url,
                'cancel_url': self.cancel_url
            },
            'transactions': [
                {
                    'item_list': {
                      'items': items,
                    },
                
                    'amount': {
                       'total': str(total),
                       'currency': self.currency
                    },
                    
                    'description': self.description
                },
            ]
        }
        return dict
    
    def as_json(self):
        return json.dumps(self.as_dict())

    def as_payment_obj(self):
        "Tworzy i zwraca obiekt Payment"
        model = get_payment_model()
        payment = model(amount = self.order.total, currency = self.currency, order = self.ext_order_obj)
        payment.backend = self.backend_config.id
        payment.save()
        self.payment_id = payment.id
        payment.change_status(model.PENDING)
        return payment
