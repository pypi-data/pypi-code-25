from requests.exceptions import HTTPError

from web_payments.forms import CreditCardPaymentFormWithName
from web_payments.utils import get_credit_card_issuer
from web_payments import PaymentStatus


class PaymentForm(CreditCardPaymentFormWithName):

    VALID_TYPES = ['visa', 'mastercard', 'discover', 'amex']
