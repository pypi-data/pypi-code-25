from paystakk.request import PaystackRequest
from paystakk.utils import build_params


class Customer(object):
    def __init__(self, **kwargs):
        self.__base = PaystackRequest(**kwargs)
        self.__url = 'https://api.paystack.co/customer'

    @property
    def ctx(self):
        return self.__base

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def customer_code(self):
        return self.ctx.data.get('customer_code', '')

    @property
    def customer_id(self):
        return self.ctx.data.get('customer_id', '')

    def __getattr__(self, item):
        return getattr(self.__base, item)

    def create_customer(self, email, first_name=None, last_name=None, phone=None, metadata=None):
        params = build_params(email=email, first_name=first_name,
                              last_name=last_name, phone=phone,
                              metadata=metadata)

        self.ctx.post(self.url, json=params)

    def fetch_customer(self, email_or_id_or_customer_code):
        """
        If there is no customer that satisfies the `email_or_id_or_customer_code`
        argument, it returns None

        :param email_or_id_or_customer_code: Customer email or customer id or customer code
        :return: dict
        """
        url_ = '{url}/{id}'.format(url=self.url, id=email_or_id_or_customer_code)
        self.ctx.get(url_)


class Invoice(object):
    def __init__(self, **kwargs):
        self.__base = PaystackRequest(**kwargs)
        self.__url = 'https://api.paystack.co/paymentrequest'

    @property
    def ctx(self):
        return self.__base

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def invoice_code(self):
        return self.ctx.data.get('invoice_code')

    @property
    def invoice_id(self):
        return self.ctx.data.get('invoice_id')

    def __getattr__(self, item):
        return getattr(self.__base, item)

    def create_invoice(self, customer, amount, due_date, description=None,
                       line_items=None, tax=None, currency='NGN',
                       metadata=None, send_notification=True, draft=False,
                       has_invoice=False, invoice_number=None):

        params = build_params(customer=customer, amount=amount,
                              due_date=due_date, description=description,
                              line_items=line_items, tax=tax, currency=currency,
                              metadata=metadata,
                              send_notification=send_notification, draft=draft,
                              has_invoice=has_invoice, invoice_number=invoice_number)

        self.ctx.post(self.url, json=params)

    def list_invoices(self, customer=None, paid=None, status=None, currency=None, include_archive=None):
        params = build_params(
            customer=customer, paid=paid, status=status, currency=currency, include_archive=include_archive)
        self.ctx.get(self.url, payload=params)


class TransferControl(object):
    def __init__(self, **kwargs):
        self.__base = PaystackRequest(**kwargs)

    def __getattr__(self, item):
        return getattr(self.__base, item)

    @property
    def ctx(self):
        return self.__base

    def get_balance(self):
        url = '{host}/balance'.format(host=self.api_url)
        self.ctx.get(url)


class PaymentPage(object):
    def __init__(self, **kwargs):
        self.__base = PaystackRequest(**kwargs)
        self._page_url = None
        self.__paystack_payment_url = 'https://paystack.com/pay'

    def __getattr__(self, item):
        return getattr(self.__base, item)

    @property
    def ctx(self):
        return self.__base

    @property
    def paystack_payment_url(self):
        return self.__paystack_payment_url

    @property
    def slug(self):
        return self.ctx.data.get('slug')

    @property
    def page_url(self):
        if self.ctx.status:
            page_url = '{http}/{slug}'.format(http=self.paystack_payment_url, slug=self.slug)
            return page_url

    @property
    def name(self):
        return self.ctx.data.get('name')

    def create_page(self, name, description=None, amount=None, slug=None, redirect_url=None, custom_fields=None):
        params = build_params(
            name=name, description=description, amount=amount, slug=slug,
            redirect_url=redirect_url, custom_fields=custom_fields)

        url = '{host}/page'.format(host=self.api_url)
        self.ctx.post(url, json=params)
