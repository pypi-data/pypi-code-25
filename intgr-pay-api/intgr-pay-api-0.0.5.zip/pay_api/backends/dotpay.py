# -*- coding: utf-8 -*-
import requests
import hashlib
import urllib
from django.conf import settings
from pay_api import get_payment_model, get_config_model, PayApiError
from django.http.response import HttpResponse

def post(request, *args, **kwargs):
    
    chk_keys = ['PIN', 'id', 'operation_number', 'operation_type',
    'operation_status', 'operation_amount',
    'operation_currency', 'operation_withdrawal_amount',
    'operation_commission_amount', 'is_completed',
    'operation_original_amount',
    'operation_original_currency', 'operation_datetime',
    'operation_related_number', 'control',
    'description', 'email', 'p_info', 'p_email',
    'credit_card_issuer_identification_number',
    'credit_card_masked_number',
    'credit_card_brand_codename',
    'credit_card_brand_code', 'credit_card_id', 'channel',
    'channel_country', 'geoip_country']
    
    incoming_data = urllib.unquote(request.body)
    data_dict = {x: y.replace('+', ' ') for x, y in (z.split('=') for z in incoming_data.split('&'))}
    
    try:
        payment = get_payment_model().objects.get(order_id = data_dict['control'])
    except get_payment_model().DoesNotExist:
        raise PayApiError("Malformed POST, order with id %s not found", data_dict['control'])
    
    payment.ext_order_id = data_dict['operation_number']
    payment.amount_paid = data_dict['operation_amount']
    
    config = get_config_model().get_config_by_backend(payment.backend)
    
    chk_str = u"" + config.receive_key
    for key in chk_keys:
        if key in data_dict.keys():
            chk_str += data_dict[key]

    assert hashlib.sha256(chk_str.encode('utf-8')).hexdigest() == data_dict['signature'], u"Malformed POST, checksum check failed"
    
    if not payment.status == payment.COMPLETED:
        if data_dict['operation_status'] == 'completed':
            payment.change_status(get_payment_model().COMPLETED)
            
        elif data_dict['operation_status'] == 'processing':
            payment.change_status(get_payment_model().PENDING)
            
        elif data_dict['operation_status'] == 'rejected':
            payment.change_status(get_payment_model().REJECTED)
            
        elif data_dict['operation_status'] == 'processing_realization_waiting':
            payment.change_status(get_payment_model().WAITING_FOR_CONFIRMATION)
            
        elif data_dict['operation_status'] == 'processing_realization':
            payment.change_status(get_payment_model().PENDING)
    
    return HttpResponse('ok', status = 200)

def create_payment(order, ext_order_obj, description, backend_config, url = settings.PAY_API_DEFAULT_NOTIFY_URL, **kwargs):
    
    if not backend_config:
        try:
            backend_config = get_config_model().objects.get(pk = settings.PAY_API_DOTPAY_DEFAULT_CONFIG_ID)
        except get_config_model().DoesNotExist():
            raise PayApiError('PAY_API_DOTPAY_DEFAULT_CONFIG_ID is invalid or not specified.')

    
    processor = PaymentProcessor(
                   order = order,
                   description = description,
                   pin = backend_config.send_key,
                   id = backend_config.shop_id,
                   ext_order_obj = ext_order_obj,
                   urlc = url,
                   backend_config = backend_config
           )
    
    return processor.create_payment_from_payment_processor_obj(processor)

class PaymentProcessor(object):
    "Klasa która służy za pośrednika między API a modelem zamówienia głównego projektu."

    def __init__(self, order, description, pin, ext_order_obj, id, urlc, **kwargs):
        self.order = order
#        self.url = order.continue_url
        self.url = 'https://test.st'
        self.type = '0'
        self.pin = pin
        self.amount = order.total
        self.currency = order.currency
        self.control = ext_order_obj.id
        self.ext_order_obj = ext_order_obj
        self.firstname = order.first_name
        self.lastname = order.last_name
        self.email = order.email
        self.id = id
        self.description = description
        self.urlc = urlc
        self.backend_config = kwargs.get('backend_config', None)
#        self.lang = 'PL'

        self.chk = self.calculate_chk()

#===============================================================================
# PIN + api_version + charset + lang + id + pid + amount + currency + description +
# control + channel + credit_card_brand + ch_lock + channel_groups + onlinetransfer +
# url + type + buttontext + urlc + firstname + lastname + email + street + street_n1 +
# street_n2 + state + addr3 + city + postcode + phone + country + code + p_info +
# p_email + n_email + expiration_date + deladdr + recipient_account_number +
# recipient_company + recipient_first_name + recipient_last_name +
# recipient_address_street + recipient_address_building + recipient_address_apartment +
# recipient_address_postcode + recipient_address_city + application +
# application_version + warranty + bylaw + personal_data + credit_card_number +
# credit_card_expiration_date_year + credit_card_expiration_date_month +
# credit_card_security_code + credit_card_store + credit_card_store_security_code +
# credit_card_customer_id + credit_card_id + blik_code + credit_card_registration +
# recurring_frequency + recurring_interval + recurring_start + recurring_count +
# surcharge_amount + surcharge + ignore_last_payment_channel + id1 + amount1 +
# currency1 + description1 + control1 + … + id(n) + amount(n) + currency(n) +
# description(n) + control(n)
#===============================================================================

    def calculate_chk(self):
        chk_string = u""
        chk_string += self.pin
#        chk_string += self.lang
        chk_string += self.id
        chk_string += "%0.2f" % (self.amount)
        chk_string += self.currency
        chk_string += self.description
        chk_string += str(self.control)
        chk_string += self.url
        chk_string += self.type
        chk_string += self.urlc
        chk_string += self.firstname
        chk_string += self.lastname
        chk_string += self.email
        return hashlib.sha256(chk_string.encode('utf-8')).hexdigest()

    def get_payload_str(self):
        for key, value in self.__dict__.items():
            if key not in ('order', 'ext_order_obj', 'backend_config', 'pin'):
                print key, value
                yield u"%s=%s" % (key, value)
            
    @classmethod
    def create_payment_from_payment_processor_obj(cls, payment_processor):
        model = get_payment_model()
        payment = model(amount = payment_processor.order.total,
                    currency = payment_processor.currency,
                    order = payment_processor.ext_order_obj,
                    ext_order_id = payment_processor.ext_order_obj.id,
                    backend = payment_processor.backend_config.id
        )
        payment.pay_link = 'https://ssl.dotpay.pl/test_payment/?' + "&".join(payment_processor.get_payload_str())
#        payment.pay_link = 'https://ssl.dotpay.pl/t2/?' + "&".join(payment_processor.get_payload_str())
        payment.save()
        print payment.pay_link
        payment.change_status(model.NEW)
        return payment.pay_link 
        
        
