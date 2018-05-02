from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
import simplejson as json
import logging

import requests
from requests.exceptions import HTTPError

from .forms import PaymentForm
from web_payments import PaymentError, PaymentStatus, RedirectNeeded
from web_payments.logic import BasicProvider
from web_payments.utils import get_credit_card_issuer

# Get an instance of a logger
logger = logging.getLogger(__name__)

CENTS = Decimal('0.01')

def authorize(fun):
    @wraps(fun)
    def wrapper(self, *args, **kwargs):
        try:
            response = fun(self, *args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 401:
                self.clear_token_cache()
                response = fun(self, *args, **kwargs)
            else:
                raise
        return response

    return wrapper


class PaypalProvider(BasicProvider):
    '''
    paypal.com payment provider
    '''
    def __init__(self, client_id, secret,
                 endpoint='https://api.sandbox.paypal.com', **kwargs):
        self.secret = secret
        self.client_id = client_id
        self.endpoint = endpoint
        self.oauth2_url = self.endpoint + '/v1/oauth2/token'
        self.payments_url = self.endpoint + '/v1/payments/payment'
        self.payment_execute_url = self.payments_url + '/%(id)s/execute/'
        self.payment_refund_url = (
            self.endpoint + '/v1/payments/capture/{captureId}/refund')
        super().__init__(**kwargs)

    def set_response_data(self, payment, response, is_auth=False):
        payment.attrs.response = response
        if 'links' in response:
            payment.attrs.links = dict(
                (link['rel'], link) for link in response['links'])

    def set_response_links(self, payment, response):
        transaction = response['transactions'][0]
        related_resources = transaction['related_resources'][0]
        resource_key = 'sale' if self._capture else 'authorization'
        links = related_resources[resource_key]['links']
        payment.attrs.links = dict((link['rel'], link) for link in links)

    @authorize
    def post(self, payment, *args, **kwargs):
        kwargs['headers'] = {
            'Content-Type': 'application/json',
            'Authorization': self.token}
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = requests.post(*args, **kwargs)
        try:
            data = response.json()
        except ValueError:
            data = {}
        if 400 <= response.status_code <= 500:
            payment.attrs.error = data
            logger.debug(data)
            message = 'Paypal error'
            if response.status_code == 400:
                error_data = response.json()
                logger.warning(message, extra={
                    'response': error_data,
                    'status_code': response.status_code})
                message = error_data.get('message', message)
            else:
                logger.warning(
                    message, extra={'status_code': response.status_code})
            payment.change_status(PaymentStatus.ERROR, message)
            raise PaymentError(message)
        else:
            self.set_response_data(payment, data)
        return data

    def get_auth_token(self, now):
        headers = {'Accept': 'application/json',
                   'Accept-Language': 'en_US'}
        post = {'grant_type': 'client_credentials'}
        response = requests.post(self.oauth2_url, data=post,
                                 headers=headers,
                                 auth=(self.client_id, self.secret))
        response.raise_for_status()
        data = response.json()

        if 'expires_in' in data:
            now += timedelta(seconds=data['expires_in'])
        return '%s %s' % (data['token_type'], data['access_token']), now

    def get_transactions_items(self, payment):
        for purchased_item in payment.get_purchased_items():
            price = purchased_item.price.quantize(
                CENTS, rounding=ROUND_HALF_UP)
            item = {'name': purchased_item.name[:127],
                    'quantity': str(purchased_item.quantity),
                    'price': str(price),
                    'currency': purchased_item.currency,
                    'sku': purchased_item.sku}
            yield item

    def get_transactions_data(self, payment):
        items = list(self.get_transactions_items(payment))
        pextras = payment.get_payment_extra()
        sub_total = (
            payment.total - pextras["delivery"] - pextras["tax"])
        sub_total = sub_total.quantize(CENTS, rounding=ROUND_HALF_UP)
        total = payment.total.quantize(CENTS, rounding=ROUND_HALF_UP)
        tax = pextras["tax"].quantize(CENTS, rounding=ROUND_HALF_UP)
        delivery = pextras["delivery"].quantize(
            CENTS, rounding=ROUND_HALF_UP)
        data = {
            'intent': 'sale' if self._capture else 'authorize',
            'transactions': [{'amount': {
                'total': str(total),
                'currency': payment.currency,
                'details': {
                    'subtotal': str(sub_total),
                    'tax': str(tax),
                    'shipping': str(delivery)}},
                'item_list': {'items': items},
                'description': pextras.get("message", "")}]}
        return data

    def get_product_data(self, payment, extra_data=None):
        data = self.get_transactions_data(payment)
        data['redirect_urls'] = {'return_url': payment.get_process_url(extra_data),
                                 'cancel_url': payment.get_process_url(extra_data)}
        data['payer'] = {'payment_method': 'paypal'}
        return data

    def get_form(self, payment, data=None):
        if not payment.id:
            payment.save()
        links = getattr(payment.attrs, "links", {})
        redirect_to = links.get('approval_url', None)
        if not redirect_to:
            payment_data = self.post(payment, self.payments_url, data=self.get_product_data(payment))
            payment.transaction_id = payment_data['id']
            redirect_to = getattr(payment.attrs, "links", {})['approval_url']
        payment.change_status(PaymentStatus.WAITING)
        raise RedirectNeeded(redirect_to['href'])

    def process_data(self, payment, request):
        success_url = payment.get_success_url()
        if not 'token' in request.GET:
            return False
        payer_id = request.GET.get('PayerID')
        if not payer_id:
            if payment.status != PaymentStatus.CONFIRMED:
                payment.change_status(PaymentStatus.REJECTED)
                raise RedirectNeeded(payment.get_failure_url())
            else:
                raise RedirectNeeded(success_url)
        executed_payment = self.execute_payment(payment, payer_id)
        self.set_response_links(payment, executed_payment)
        payment.attrs.payer_info = executed_payment['payer']['payer_info']
        if self._capture:
            payment.captured_amount = payment.total
            payment.change_status(PaymentStatus.CONFIRMED)
        else:
            payment.change_status(PaymentStatus.PREAUTH)
        raise RedirectNeeded(success_url)

    def execute_payment(self, payment, payer_id):
        post = {'payer_id': payer_id}
        links = getattr(payment.attrs, "links", {})
        execute_url = links['execute']['href']
        return self.post(payment, execute_url, data=post)

    def get_amount_data(self, payment, amount=None):
        return {
            'currency': payment.currency,
            'total': str(amount.quantize(
                CENTS, rounding=ROUND_HALF_UP))}

    def capture(self, payment, amount=None, final=True):
        if amount is None:
            amount = payment.total
        amount_data = self.get_amount_data(payment, amount)
        capture_data = {
            'amount': amount_data,
            'is_final_capture': final
        }
        links = getattr(payment.attrs, "links", {})
        url = links['capture']['href']
        try:
            capture = self.post(payment, url, data=capture_data)
        except HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = {}
            if error.get('name') != 'AUTHORIZATION_ALREADY_COMPLETED':
                raise e
            capture = {'state': 'completed'}
        state = capture['state']
        if state == 'completed':
            payment.change_status(PaymentStatus.CONFIRMED)
            return amount
        elif state in ['partially_captured', 'partially_refunded']:
            return amount
        elif state == 'pending':
            payment.change_status(PaymentStatus.WAITING)
        elif state == 'refunded':
            payment.change_status(PaymentStatus.REFUNDED)
            raise PaymentError('Payment already refunded')

    def release(self, payment):
        links = getattr(payment.attrs, "links", {})
        url = links['void']['href']
        self.post(payment, url)

    def refund(self, payment, amount=None):
        if amount is None:
            amount = payment.captured_amount
        amount_data = self.get_amount_data(payment, amount)
        refund_data = {'amount': amount_data}
        links = getattr(payment.attrs, "links", {})
        url = links['refund']['href']
        self.post(payment, url, data=refund_data)
        payment.change_status(PaymentStatus.REFUNDED)
        return amount


class PaypalCardProvider(PaypalProvider):
    '''
    paypal.com credit card payment provider
    '''

    def get_form(self, payment, data=None):
        if payment.status == PaymentStatus.WAITING:
            payment.change_status(PaymentStatus.INPUT)
        form = PaymentForm(formdata=data, provider=self, payment=payment)
        if data and form.validate():
            cleaned_data = form.data
            card_type = get_credit_card_issuer(cleaned_data['number'])[0]
            product_data = self.get_product_data(payment, cleaned_data)
            try:
                data = self.post(payment, self.payments_url, data=product_data)
            except HTTPError as e:
                response = e.response
                if response.status_code == 400:
                    error_data = e.response.json()
                    errors = [
                        error['issue'] for error in error_data['details']]
                else:
                    errors = ['Internal PayPal error']
                payment.change_status(PaymentStatus.ERROR, errors)
                raise PaymentError("Paypal Error")
            else:
                payment.transaction_id = data['id']
                self.set_response_links(payment, data)
                if self._capture:
                    payment.captured_amount = payment.total
                    payment.change_status(PaymentStatus.CONFIRMED)
                else:
                    payment.change_status(PaymentStatus.PREAUTH)
            raise RedirectNeeded(payment.get_success_url())
        return form

    def get_product_data(self, payment, extra_data):
        data = self.get_transactions_data(payment)
        number = extra_data['number']
        card_type, _card_issuer = get_credit_card_issuer(number)
        credit_card = {'number': number,
                       'type': card_type,
                       'expire_month': extra_data['expiration'].month,
                       'expire_year': extra_data['expiration'].year}
        if extra_data.get('cvv2', None):
            credit_card['cvv2'] = extra_data['cvv2']
        data['payer'] = {'payment_method': 'credit_card',
                         'funding_instruments': [{'credit_card': credit_card}]}
        return data

    def process_data(self, payment, request):
        return False
