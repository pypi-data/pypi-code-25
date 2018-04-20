# Copyright 2018 Locl Interactive Inc. (d/b/a Meya.ai). All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from marshmallow import Schema, fields, validate
from meyacards.base import Card
from meyacards.utilities import turn_into_sentences


class Element(object):

    class Schema(Schema):
        title = fields.Str(
            required=True, validate=validate.Length(max=50))
        subtitle = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=50))
        quantity = fields.Integer(required=False, allow_none=True)
        price = fields.Float(required=False, allow_none=True)
        currency = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=50))
        image_url = fields.Url(required=False, allow_none=True)

    def __init__(self, data):
        self.title = data.get('title')
        self.subtitle = data.get('subtitle')
        self.quantity = data.get('quantity')
        self.price = data.get('price')
        self.currency = data.get('currency')
        self.image_url = data.get('image_url')


class Adjustment(object):

    class Schema(Schema):
        name = fields.Str(max_length=50)
        amount = fields.Float()

    def __init__(self, data):
        self.name = data.get('name')
        self.amount = data.get('amount')


class Address(object):

    class Schema(Schema):
        street_1 = fields.Str(
            required=True, validate=validate.Length(max=1024))
        street_2 = fields.Str(
            required=False, allow_none=True,
            validate=validate.Length(max=1024))
        city = fields.Str(
            required=True, validate=validate.Length(max=1024))
        postal_code = fields.Str(
            required=True, validate=validate.Length(max=50))
        state = fields.Str(
            required=True, validate=validate.Length(max=100))
        country = fields.Str(
            required=True, validate=validate.Length(max=100))

    def __init__(self, data):
        self.street_1 = data.get('street_1')
        self.street_2 = data.get('street_2')
        self.city = data.get('city')
        self.postal_code = data.get('postal_code')
        self.state = data.get('state')
        self.country = data.get('country')


class Summary(object):

    class Schema(Schema):
        subtotal = fields.Float(required=False, allow_none=True)
        shipping_cost = fields.Float(required=False, allow_none=True)
        total_tax = fields.Float(required=False, allow_none=True)
        total_cost = fields.Float(required=True, allow_none=True)

    def __init__(self, data):
        self.subtotal = data.get('subtotal')
        self.shipping_cost = data.get('shipping_cost')
        self.total_tax = data.get('total_tax')
        self.total_cost = data.get('total_cost')


class Receipt(Card):
    type = "receipt"

    class Schema(Card.Schema):
        # primitive elements
        recipient_name = fields.Str(
            required=True, validate=validate.Length(max=512))
        order_number = fields.Str(
            required=True, validate=validate.Length(max=256))
        currency = fields.Str(
            required=True, validate=validate.Length(max=20))
        payment_method = fields.Str(
            required=True, validate=validate.Length(max=20))
        timestamp = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=100))
        order_url = fields.Url(required=False, allow_none=True)

        # nested elements
        elements = fields.Nested(Element.Schema, many=True, required=True)
        address = fields.Nested(
            Address.Schema, required=False, allow_none=True)
        summary = fields.Nested(Summary.Schema, required=True)
        adjustments = fields.Nested(
            Adjustment.Schema, many=True, required=False, allow_none=True)

    def __init__(self, payload=None, **kwargs):
        super(Receipt, self).__init__(payload=payload, **kwargs)
        self.recipient_name = self.payload.get('recipient_name')
        self.order_number = self.payload.get('order_number')
        self.currency = self.payload.get('currency')
        self.payment_method = self.payload.get('payment_method')
        self.subtotal = self.payload.get('subtotal')
        self.shipping_cost = self.payload.get('shipping_cost')
        self.total_tax = self.payload.get('total_tax')
        self.total_cost = self.payload.get('total_cost')

        self.elements = []
        _elements = self.payload.get('elements')
        if _elements:
            for element_data in _elements:
                self.elements.append(Element(element_data))

        self.street_1 = self.payload.get('street_1')
        self.street_2 = self.payload.get('street_2')
        self.city = self.payload.get('city')
        self.postal_code = self.payload.get('postal_code')
        self.state = self.payload.get('state')
        self.country = self.payload.get('country')

        self.timestamp = self.payload.get('timestamp')
        self.order_url = self.payload.get('order_url')

        self.adjustments = []
        _adjustments = self.payload.get('adjustments')
        if _adjustments:
            for adjustment_data in _adjustments:
                self.adjustments.append(Adjustment(adjustment_data))

    def as_text(self):
        strs = [self.recipient_name, self.payment_method, self.order_number]
        return turn_into_sentences(strs)
