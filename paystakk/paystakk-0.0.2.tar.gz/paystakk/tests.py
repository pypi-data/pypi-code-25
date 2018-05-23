
from unittest import TestCase

import time

from paystakk.utils import build_params
from paystakk.api import TransferControl, PaymentPage, Customer, Invoice

SECRET_KEY = 'YOUR_PAYSTACK_KEY'
PUBLIC_KEY = 'YOUR_PAYSTACK_KEY'


class TestCustomer(TestCase):
	def setUp(self):
		self.api = Customer(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		self.api.create_customer(email='test@example.com')
		self.customer_id = self.api.customer_id
		self.customer_code = self.api.customer_code

	def test_create_customer(self):
		self.assertEqual(self.api.ctx.status, True)

	def test_fetch_customer(self):
		self.api.fetch_customer(email_or_id_or_customer_code='test@example.com')
		self.assertEqual(self.customer_code, self.api.customer_code)
		self.assertEqual(self.customer_id, self.api.customer_id)
		self.assertEqual(True, self.api.ctx.status)

		self.api.fetch_customer(email_or_id_or_customer_code='not@example.com')
		self.assertEqual(False, self.api.ctx.status)
		self.assertEqual(self.api.customer_id, '')
		self.assertEqual(self.api.customer_code, '')


class TestInvoice(TestCase):
	def setUp(self):
		self.api = Customer(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		self.api.create_customer(email='test@example.com')
		self.customer_code = self.api.customer_code

	def test_create_invoice(self):
		api = Invoice(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		api.create_invoice(customer=self.customer_code, amount=500000, due_date='2020-12-20')

		self.assertEqual(self.api.ctx.status, True)

	def test_list_invoices(self):
		api = Invoice(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		api.list_invoices()

		self.assertEqual(api.ctx.status, True)


class TestTransferControl(TestCase):
	def test_balance(self):
		api = TransferControl(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		api.get_balance()

		self.assertEqual(api.ctx.status, True)
		self.assertEqual(api.ctx.message, 'Balances retrieved')


class TestPaymentPage(TestCase):
	def test_create_page(self):
		r = PaymentPage(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		slug = str(time.time())
		r.create_page(name='test page', slug=slug)

		self.assertEqual(r.ctx.status, True)
		self.assertEqual(r.ctx.message, 'Page created')
		self.assertEqual(r.name, 'test page')
		self.assertEqual(r.slug, slug)
		self.assertEqual(r.page_url, 'https://paystack.com/pay/{slug}'.format(slug=slug))


class TestFunctions(TestCase):
	def test_build_params(self):
		self.assertEqual(build_params(one=1, two=2), {'one': 1, 'two': 2})
		self.assertEqual(build_params(), {})
		self.assertEqual(build_params(a='a', b=None, c='b'), {'a': 'a', 'c': 'b'})
