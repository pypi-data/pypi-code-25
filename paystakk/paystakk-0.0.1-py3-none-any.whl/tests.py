
from unittest import TestCase

import time

import six

from paystakk.utils import build_params
from paystakk.api import TransferControl, PaymentPage, Customer, Invoice

SECRET_KEY = 'sk_test_04d09de6922fa975afdc7b5eb40ff357e74b9f01'
PUBLIC_KEY = 'pk_test_666fbd4fca373a2a88ec13f6f22dfb46cbdec709'


class TestCustomer(TestCase):
	def setUp(self):
		self.paystack = Customer(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		self.customer = self.paystack.create_customer(email='test@example.com')

	def test_create_customer(self):
		self.assertEqual(self.customer['status'], True)

	def test_fetch_customer(self):
		customer = self.paystack.fetch_customer(email_or_id_or_customer_code='test@example.com')
		customer2 = self.paystack.fetch_customer(email_or_id_or_customer_code='not@example.com')

		self.assertEqual(self.paystack.customer_code, customer['data']['customer_code'])
		self.assertEqual(self.paystack.customer_id, customer['data']['id'])
		self.assertEqual(customer2['status'], False)


class TestInvoice(TestCase):
	def setUp(self):
		self.paystack = Customer(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		self.customer = self.paystack.create_customer(email='test@example.com')

	def test_create_invoice(self):
		paystack = Invoice(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		invoice = paystack.create_invoice(
			customer=self.paystack.customer_code, amount=500000, due_date='2020-12-20'
		)

		self.assertEqual(invoice['status'], True)

	def test_list_invoices(self):
		api = Invoice(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		invoices = api.list_invoices()

		self.assertEqual(invoices['status'], True)


class TestTransferControl(TestCase):
	def test_balance(self):
		page = TransferControl(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		balance = page.get_balance()

		self.assertEqual(balance['status'], True)
		self.assertEqual(balance['message'], 'Balances retrieved')


class TestPaymentPage(TestCase):
	def test_create_page(self):
		r = PaymentPage(secret_key=SECRET_KEY, public_key=PUBLIC_KEY)
		slug = six.text_type(time.time())
		page = r.create_page(name='test page', slug=slug)

		self.assertEqual(page['status'], True)
		self.assertEqual(page['message'], 'Page created')
		self.assertEqual(page['data']['name'], 'test page')
		self.assertEqual(page['data']['slug'], slug)
		self.assertEqual(r.page_url, 'https://paystack.com/pay/{slug}'.format(slug=slug))


class TestFunctions(TestCase):
	def test_build_params(self):
		self.assertEqual(build_params(one=1, two=2), {'one': 1, 'two': 2})
		self.assertEqual(build_params(), {})
		self.assertEqual(build_params(a='a', b=None, c='b'), {'a': 'a', 'c': 'b'})
