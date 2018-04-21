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


def post(request, *args, **kwargs):
    model = get_payment_model()

    print "##########"
    print request.body
    print "##########"
    
    try:
        data = json.loads(request.body)
        header = request.META['HTTP_OPENPAYU_SIGNATURE']
    except KeyError:
        return HttpResponse("not ok", status = 500)

    header_data_raw = header.split(';')
    header_data = {}
    for x in header_data_raw:
        key, value = x.split('=')[0], x.split('=')[1]
        header_data[key] = value

    try:
        payment = model.objects.get(ext_order_id = data['order']['orderId'])
#        payment = model.objects.get(id = data['order']['orderId'].split('-')[0])
    except model.DoesNotExist:
#        raise PayApiError('PaymentDoesNotExist (local?) ext_order_id (%s)' % data['order']['orderId'])
        return HttpResponse("not ok", status = 200)

    incoming_signature = header_data['signature']
    algorithm = header_data['algorithm']

    config = get_config_model().get_config_by_backend(payment.backend)

    if algorithm == 'MD5':
        m = hashlib.md5()
        key = config.receive_key
        signature = request.body + str(key)
        m.update(signature)
        signature = m.hexdigest()
        
        if incoming_signature == signature and not payment.status == model.COMPLETED:
            status = data['order']['status']
            payment.change_status(new_status = getattr(model, status))
            payment.amount_paid = Decimal(data['order']['totalAmount']) / Decimal(100)
            payment.save()

        return HttpResponse("ok", status = 200)
            
    else:
        return HttpResponse("not ok", status = 500)

def get_paymethods(backend_config = None, ignored = []):
    
    if not backend_config:
        try:
            backend_config = get_config_model().objects.get(pk = settings.PAY_API_PAYU_DEFAULT_CONFIG_ID)
        except get_config_model().DoesNotExist():
            raise PayApiError('PAY_API_PAYU_DEFAULT_CONFIG_ID is invalid or not specified.')
    
    api = PayuApi(pos_id = backend_config.shop_id, client_secret = backend_config.send_key)
    result = api.get_paymethod_tokens()
    result['payByLinks'] = [x for x in result['payByLinks'] if x['value'] not in ignored]
    
    return result

def create_payment(order, ext_order_obj, description, backend_config, url = settings.PAY_API_DEFAULT_NOTIFY_URL, **kwargs):
    assert 'customer_ip' in kwargs.keys(), "Customer IP must be specified for PayU backend"
    
    if not backend_config:
        try:
            backend_config = get_config_model().objects.get(pk = settings.PAY_API_PAYU_DEFAULT_CONFIG_ID)
        except get_config_model().DoesNotExist():
            raise PayApiError('PAY_API_PAYU_DEFAULT_CONFIG_ID is invalid or not specified.')
    
    processor = PaymentProcessor(
                 order = order,
                 description = description,
                 customer_ip = kwargs.get('customer_ip'),
                 ext_order_obj = ext_order_obj,
                 pos_id = backend_config.shop_id,
                 client_secret = backend_config.send_key,
                 backend_config = backend_config,
           )
    
    processor.add_order_items(order.order_items)
    processor.set_buyer_data(order.first_name, order.last_name, order.email, order.phone) # lang code, default pl
    
    paymethod_value = kwargs.get('paymethod_value', None)
    paymethod_type = kwargs.get('paymethod_type', None)
    
    if paymethod_value and paymethod_type:
        processor.set_paymethod(value = paymethod_value, type = paymethod_type)
    elif paymethod_value:
        processor.set_paymethod(value = paymethod_value)
    
    validity_time = kwargs.get('validity_time', None)
    if validity_time:
        processor.set_validity_time(validity_time)

    continue_url = order.__dict__.get('continue_url', None)
    if continue_url:
        processor.set_continue_url(order.continue_url)
    
    return processor.create_payment_from_payment_processor_obj(processor)

class PayuApi(object):
    "Klasa odpowiedzialna za komunikację z PayU REST Api"

    def __init__(self, pos_id = settings.PAY_API_POS_ID, client_secret = settings.PAY_API_CLIENT_SECRET, grant_type = 'client_credentials'):
        self.payu_auth_url = settings.PAY_API_AUTH_URL
        self.payu_delete_token_url = settings.PAY_API_DELETE_TOKEN_URL
        self.payu_api_order_url = settings.PAY_API_ORDER_URL
        self.payu_api_paymethods_url = settings.PAY_API_PAYMETHODS_URL

        self.pos_id = pos_id
        self.token = self.get_access_token(pos_id, client_secret, grant_type)

    # Methods for authenticating our API connection (getting token)

    def get_access_token(self, client_id, client_secret, grant_type):
        "Metoda która pobiera access_token potrzebny do dalszej komunikacji z API"

        payu_auth_url = self.payu_auth_url
        
        data = {
            'grant_type': grant_type,
            'client_id': client_id,
            'client_secret': client_secret,
        }
        
        headers = {
           'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(payu_auth_url, data = data, headers = headers)

        try:
            return json.loads(response.text)['access_token']
        except KeyError:
            raise PayApiError(response.text)

    def delete_token(self):
        "Metoda która dezaktywuje access_token"

        payu_delete_token_url = self.payu_delete_token_url + self.token
        headers = {
          'Authorization': 'Bearer %s' % self.token,
        }

        response = requests.delete(payu_delete_token_url, headers = headers)
        self.token = None

        return (response.status_code == 204)

    # Close API instance if no longer needed

    def close(self):
        "Metoda wywoływana na instancji PayuApi zamykająca połączenie (usuwa token)"
        self.delete_token()

    # Method for sending an order (creates a Payment object, return redirectUrl)

    def create_order(self, payment_processor):
        "Metoda tworząca zamówienie i zwracająca link do przekierowania"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token,
        }

        payment = payment_processor.as_payment_obj()
        payment_processor.pos_id = self.pos_id
        
        for p in get_payment_model().objects.filter(order_id = payment.order_id).exclude(id = payment.id).exclude(status = get_payment_model().COMPLETED):
            if p.ext_order_id:
                self.reject_order(p.ext_order_id)
        
        response = requests.post(self.payu_api_order_url, data = payment_processor.as_json(), headers = headers, allow_redirects = False)
        response_dict = json.loads(response.text)
        self.close()

        try:
            payment.ext_order_id = response_dict[u'orderId']
            if response_dict[u'status'][u'statusCode'] == u'SUCCESS':
                if 'redirectUri' in response_dict:
                    payment.pay_link = response_dict['redirectUri']

                payment.save()
                return {'cvv': None, 'redirectUrl': payment.pay_link}
            
            elif response_dict[u'status'][u'statusCode'] == u'WARNING_CONTINUE_3DS':
                payment.save()
                return {'cvv': None, 'redirectUrl': response_dict['redirectUri']}
        
            elif response_dict[u'status'][u'statusCode'] == u'WARNING_CONTINUE_CVV':
                payment.save()
                return {'cvv': response_dict[u'redirectUri'], 'redirectUrl': None}
            
            elif response_dict[u'status'][u'statusCode'] == u'WARNING_CONTINUE_REDIRECT':
                payment.save()
                return {'cvv': None, 'redirectUrl': response_dict['redirectUri']}
                
            else:
                raise PayApiError(response.text)

        except KeyError as e:
            return {}

    # Method that returns all pay methods

    def get_paymethod_tokens(self):
        "Metoda pobierająca dostępne metody płatności dla POS'a"

        headers = {
          'Authorization': 'Bearer %s' % self.token
        }

        response = requests.get(self.payu_api_paymethods_url, headers = headers)
        result = json.loads(response.text)
        
        if result[u'status'][u'statusCode'] == u'SUCCESS':
            return result
        else:
            return None

    # Method that rejects the order

    def reject_order(self, ext_order_id):
        "Metoda anulująca zamówienie"

        headers = {
            'Authorization': 'Bearer %s' % self.token,
        }

        url = self.payu_api_order_url
        if url.endswith('/'):
            url += ext_order_id
        else:
            url += '/'
            url += ext_order_id

        try:
            # Aby skutecznie zwrócić środki do płacącego, w przypadku zamówienia w statusie
            # WAITING_FOR_CONFIRMATION należy wykonać dwa żądania DELETE.
            # http://developers.payu.com/pl/restapi.html#cancellation
            response1 = json.loads(requests.delete(url, headers = headers).text)
            response2 = json.loads(requests.delete(url, headers = headers).text)

            if response1['status']['statusCode'] == response2['status']['statusCode'] == 'SUCCESS':
                model = get_payment_model()
#                model.objects.get(ext_order_id = ext_order_id).change_status(model.REJECTED)

                return True
            else:
                raise PayApiError(response1.text, response2.text)
        except:
            return False

class PaymentProcessor(object):
    "Klasa która służy za pośrednika między API a modelem zamówienia głównego projektu."

    def __init__(self, **kwargs):
        self.order = kwargs.get('order')
        self.notify_url = kwargs.get('notify_url', settings.PAY_API_DEFAULT_NOTIFY_URL)
        self.currency = kwargs.get('currency', settings.PAY_API_CURRENCY)
        self.payment_id = None
        self.description = kwargs.get('description')
        self.customer_ip = kwargs.get('customer_ip')
        self.ext_order_obj = kwargs.get('ext_order_obj')
        self.backend_config = kwargs.get('backend_config')
        self.pos_id = kwargs.get('pos_id')
        self.client_secret = kwargs.get('client_secret')
        self.order_items = []
        self.external_id = None

    def add_order_items(self, obj):
        "Dodaj pozycje zamówienia, przyjmuje instancje klasy OrderItem"
        if isinstance(obj, OrderItem):
            self.order_items.append(obj)
        elif isinstance(obj, type([])):
            self.order_items.extend(obj)
        else:
            raise PayApiError("Zły format order_item. Funkcja add_order_items przyjmuje obiekt OrderItem lub listę złożoną z instancji klasy OrderItem.")

    def set_paymethod(self, value, type = "PBL", **kwargs):
        "Ustaw metodę płatności, przy przezroczystej integracji. Na podstawie PayuApi.get_paymethod_tokens()"
        if not hasattr(self, 'paymethods'):
            self.paymethods = {}
            self.paymethods['payMethod'] = {'type': type, 'value': value}

    def set_buyer_data(self, first_name, last_name, email, phone, lang_code = 'pl'):
        "Ustaw dane kupującego"
        if not hasattr(self, 'buyer'):
            self.buyer = {
                'email': email,
                'phone': phone,
                'firstName': first_name,
                'lastName': last_name,
                'language': lang_code
            }

    def set_continue_url(self, continue_url):
        "Ustaw link na który użytkownik zostanie przekierowany po płatności"
        if not hasattr(self, 'continueUrl'):
            self.continueUrl = continue_url

    def set_validity_time(self, validity_time = 60 * 60 * 24 * 5): # 5 days
        "Ustaw czas wygaśnięcia linku do płatności (przy PayUbyLink)"
        if not hasattr(self, 'validityTime'):
            self.validityTime = int(validity_time)

    def as_json(self):
        "Zwraca zawartość obiektu do formatu json w formacie przyjmowanym przez PayU"
        total = Decimal(0)
        products = []


        for i in self.order_items:
            total += Decimal(i.unit_price) * Decimal(i.quantity)
            i.sub_unit = settings.PAY_API_CURRENCY_DATA[self.currency]['sub_unit']
            products.append(i.as_dict())

        self.total = int(self.order.total * settings.PAY_API_CURRENCY_DATA[self.currency]['sub_unit'])

        json_dict = {
            'notifyUrl': self.notify_url,
            'customerIp': self.customer_ip,
            'extOrderId': "%s-%s" % (self.payment_id, hashlib.md5("%s" % timezone.now()).hexdigest()[:5]),
            'merchantPosId': self.pos_id,
            'description': self.description,
            'currencyCode': self.currency,
            'totalAmount': self.total,
            'products': products,
        }
        
        # additional data
        if hasattr(self, 'paymethods'):
            json_dict['payMethods'] = self.paymethods

        if hasattr(self, 'buyer'):
            json_dict['buyer'] = self.buyer

        if hasattr(self, 'continueUrl'):
            json_dict['continueUrl'] = self.continueUrl

        if hasattr(self, 'validityTime'):
            json_dict['validityTime'] = self.validityTime

        return json.dumps(json_dict)

    def as_payment_obj(self):
        "Tworzy i zwraca obiekt Payment"
        model = get_payment_model()
        payment = model(amount = self.order.total, currency = self.currency, order = self.ext_order_obj)
        if hasattr(self, 'validityTime'):
            payment.pay_link_valid_until = timezone.now() + timezone.timedelta(seconds = self.validityTime)
        payment.backend = self.backend_config.id
        payment.save()
        self.payment_id = payment.id
        payment.change_status(model.NEW)
        return payment
    
    @classmethod
    def create_payment_from_payment_processor_obj(cls, payment_processor):
        api = PayuApi(pos_id = payment_processor.pos_id, client_secret = payment_processor.client_secret)
        return api.create_order(payment_processor)
