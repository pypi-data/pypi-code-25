from paystakk.request import PaystackRequest
from paystakk.utils import build_params


class Customer(object):
    def __init__(self, **kwargs):
        self._base = PaystackRequest(**kwargs)
        self.__url = 'https://api.paystack.co/customer'
        self.__customer_code = None
        self.__customer_id = None

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def customer_code(self):
        return self.__customer_code

    @customer_code.setter
    def customer_code(self, value):
        self.__customer_code = value

    @property
    def customer_id(self):
        return self.__customer_id

    @customer_id.setter
    def customer_id(self, value):
        self.__customer_id = value

    def __getattr__(self, item):
        return getattr(self._base, item)

    def create_customer(self, email, first_name=None, last_name=None, phone=None, metadata=None):
        params = build_params(
            email=email, first_name=first_name, last_name=last_name,
            phone=phone, metadata=metadata
        )
        customer = self.post(self.url, json=params)
        self.customer_code = customer['data']['customer_code']
        self.customer_id = customer['data']['id']

        return customer

    def fetch_customer(self, email_or_id_or_customer_code):
        """
        If there is no customer that satisfies the `email_or_id_or_customer_code`
        argument, it returns None

        :param email_or_id_or_customer_code: Customer email or customer id or customer code
        :return: dict
        """
        url_ = '{url}/{id}'.format(url=self.url, id=email_or_id_or_customer_code)
        customer = self.get(url_)

        if customer['status']:
            self.customer_code = customer['data']['customer_code']
            self.customer_id = customer['data']['id']

        return customer


class Invoice(object):
    def __init__(self, **kwargs):
        self._base = PaystackRequest(**kwargs)
        self.__url = 'https://api.paystack.co/paymentrequest'
        self.__invoice_code = None
        self.__invoice_id = None
        self.__customer_cls = Customer(**kwargs)

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def invoice_code(self):
        return self.__invoice_code

    @invoice_code.setter
    def invoice_code(self, value):
        self.__invoice_code = value

    @property
    def invoice_id(self):
        return self.__invoice_id

    @invoice_id.setter
    def invoice_id(self, value):
        self.__invoice_id = value

    def __getattr__(self, item):
        return getattr(self._base, item)

    def create_invoice(
            self, customer, amount, due_date, description=None,
            line_items=None, tax=None, currency='NGN', metadata=None,
            send_notification=True, draft=False, has_invoice=False,
            invoice_number=None
    ):
        params = build_params(
            customer=customer, amount=amount, due_date=due_date,
            description=description, line_items=line_items, tax=tax,
            currency=currency, metadata=metadata,
            send_notification=send_notification, draft=draft,
            has_invoice=has_invoice, invoice_number=invoice_number
        )
        invoice = self.post(self.url, json=params)

        self.invoice_code = invoice['data']['request_code']
        self.invoice_id = invoice['data']['id']

        return invoice

    def list_invoices(self, customer=None, paid=None, status=None, currency=None, include_archive=None):
        params = build_params(
            customer=customer, paid=paid, status=status, currency=currency, include_archive=include_archive)
        invoices = self.get(self.url, payload=params)

        return invoices


class TransferControl(object):
    def __init__(self, **kwargs):
        self._base = PaystackRequest(**kwargs)

    def __getattr__(self, item):
        return getattr(self._base, item)

    def get_balance(self):
        url = '{host}/balance'.format(host=self.api_url)
        r = self.get(url)

        return r


class PaymentPage(object):
    def __init__(self, **kwargs):
        self._base = PaystackRequest(**kwargs)
        self._page_url = None
        self.__paystack_payment_url = 'https://paystack.com/pay'

    def __getattr__(self, item):
        return getattr(self._base, item)

    @property
    def paystack_payment_url(self):
        return self.__paystack_payment_url

    @property
    def page_url(self):
        return self._page_url

    @page_url.setter
    def page_url(self, value):
        self._page_url = value

    def create_page(self, name, description=None, amount=None, slug=None, redirect_url=None, custom_fields=None):
        params = build_params(
            name=name, description=description, amount=amount, slug=slug,
            redirect_url=redirect_url, custom_fields=custom_fields
        )

        url = '{host}/page'.format(host=self.api_url)
        page = self.post(url, json=params)

        # no need to do any checks since `self.post` would have raised an
        # exception if page was not created
        page_slug = page['data']['slug']
        page_url = '{http}/{slug}'.format(http=self.paystack_payment_url, slug=page_slug)
        self.page_url = page_url

        return page
