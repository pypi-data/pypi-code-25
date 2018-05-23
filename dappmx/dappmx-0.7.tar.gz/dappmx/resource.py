from dappmx.api_client import APIClient
import urllib


class _Resource(object):
    def __init__(self, attributes):
        self.initialize_instance(attributes)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    @classmethod
    def class_name(cls):
        try:
            return "%s" % urllib.parse.quote_plus(cls.__name__.lower())
        except AttributeError:
            return "%s" % urllib.quote_plus(cls.__name__.lower())

    @classmethod
    def class_url(cls):
        return "%ss/" % cls.class_name()

    def instance_url(self):
        return "%s/%s" % (self.class_url(), self.id)

    def initialize_instance(self, attributes):
        if 'id' in attributes.keys():
            self.id = attributes['id']

        existing_keys = self.__dict__.keys()
        new_keys = attributes.keys()

        old_keys = set(existing_keys) - set(new_keys)
        for key in old_keys:
            self.__dict__[key] = None

        for key in new_keys:
            self.__dict__[key] = attributes[key]

    @classmethod
    def load_url(cls, path, method='GET', params=None, api_version=None,
                 merchant_id=None, api_key=None):
        response = APIClient.request(method, path, params, _api_version=api_version,
                                     _merchant_id=merchant_id, _api_key=api_key)
        return response

    def load_with_request(self, url=None, method='POST', params=None, api_version=None,
                          merchant_id=None, api_key=None):
        if url is None:
            url = self.instance_url()
            method = 'GET'

        response = self.load_url(url, method=method, params=params, api_version=api_version,
                                 merchant_id=merchant_id, api_key=api_key)

        self.initialize_instance(response)

        return self


class _CreatableResource(_Resource):

    @classmethod
    def create(cls, params, api_version=None, merchant_id=None, api_key=None):
        endpoint = cls.class_url()
        return cls(cls.load_url(endpoint, method='POST', params=params,
                                api_version=api_version,
                                merchant_id=merchant_id, api_key=api_key))


class _RetrievableResource(_Resource):

    @classmethod
    def retreive(cls, _id, api_version=None, merchant_id=None, api_key=None):
        endpoint = cls.class_url()
        return cls(cls.load_url("%s%s" % (endpoint, _id),
                                api_version=api_version,
                                merchant_id=merchant_id, api_key=api_key))


class DappCode(_CreatableResource, _RetrievableResource):

    @classmethod
    def class_name(cls):
        return "dapp-code"

    def payment(self, api_version=None, merchant_id=None, api_key=None):
        data = DappCode.load_url("%s/payment" % (self.instance_url()),
                                 api_version=api_version,
                                 merchant_id=merchant_id, api_key=api_key)

        if data is None:
            return None

        return Payment(data)


class Card(_CreatableResource, _RetrievableResource):

    @classmethod
    def create(cls, params, api_version=None, merchant_id=None, api_key=None):
        from dappmx.encrypt import encrypt_rsa
        for key, value in params.items():
            if key in ["card_number", "cardholder", "cvv",
                       "exp_month", "exp_year", "email", "phone_number"]:
                params[key] = encrypt_rsa(value)

        return super().create(params, api_version, merchant_id, api_key)


class Payment(_CreatableResource, _RetrievableResource):

    def refund(self, api_version=None, merchant_id=None, api_key=None):
        payment = self.load_with_request("%s/refund" % (self.instance_url()),
                                         'POST', api_version=api_version,
                                         merchant_id=merchant_id, api_key=api_key)

        return payment
