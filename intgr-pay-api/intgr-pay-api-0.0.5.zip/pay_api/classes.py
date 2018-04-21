# -*- coding: utf-8 -*-
import json
import ast
from decimal import Decimal
from pay_api import PayApiError
from django.conf import settings
import importlib 

class OrderItem(object):
    "Klasa która służy jako pośrednik między pozycjami zamówienia a PaymentProcessorem"

    def __init__(self, *args, **kwargs):
        self.quantity = '1'
        self.name = kwargs.get('name', '')
        self.unit_price = kwargs.get('unit_price')
        self.quantity = kwargs.get('quantity', '1')

    def as_dict(self):
        return {
           'name': self.name,
           'unitPrice': str(int(Decimal(self.unit_price) * Decimal(self.sub_unit))),
           'quantity': self.quantity
        }

class Order(object):

    def __init__(self, *args, **kwargs):
        self.order_items = []
        self.ext_order_obj = kwargs.get('ext_order_obj')
        self.currency = kwargs.get('currency', 'PLN')
        self.first_name = kwargs.get('first_name', None)
        self.last_name = kwargs.get('last_name', None)
        self.email = kwargs.get('email', None)
        self.phone = kwargs.get('phone', None)
        self.continue_url = kwargs.get('continue_url', None)
        self.cancel_url = kwargs.get('cancel_url', None)
        
    def add_order_item(self, order_item):
        if type(order_item) == OrderItem:
            self.order_items.append(order_item)
        elif type(order_item) == type([]):
            for item in order_item:
                if type(item) == OrderItem:
                    self.order_items.append(item)
                else:
                    raise PayApiError("add_order_item function accepts only objects of type OrderItem or a list of those objects.")
                    
        else:
            raise PayApiError("add_order_item function accepts only objects of type OrderItem or a list of those objects.")
            
    @property 
    def total(self):
        sum = Decimal(0)
        for item in self.order_items:
            sum += Decimal(item.quantity) * Decimal(item.unit_price)
        return sum

    def create_payment(self, ext_order_obj, description = '', backend_name = None, backend_config = None, **kwargs):
        try:
            backend = importlib.import_module('pay_api.backends.%s' % backend_name)
        except ImportError:
            raise PayApiError("No backend %s found. Try another one or create one." % backend_name)
        
        return backend.create_payment(self, ext_order_obj, description, backend_config, **kwargs)
        
        
        
