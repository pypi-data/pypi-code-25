import hashlib
import hmac
import requests
from datetime import datetime

class Client:

    def __init__(self, merchant_code, api_secret_key):
        """Initialize a Avantage Rest API Client.

           Arguments:
           merchant_code  -- Your merchant identifier (received from Avangate).
           api_secret_key -- Your unique Avangate supplied api secret key.
        """
        self.baseUrl = None
        self.merchantCode = merchant_code
        self.apiSecretKey = api_secret_key
        self.date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def set_base_url(self, base_url):
        self.baseUrl = base_url

    def get(self, url):
        return self.execute('GET', url)

    def post(self, url):
        return self.execute('POST', url)

    def put(self, url):
        return self.execute('PUT', url)

    def delete(self, url):
        return self.execute('DELETE', url)

    def __create_hash(self):
        auth_key = "{}{}{}{}".format(len(self.merchantCode), self.merchantCode, \
                                     len(str(self.date)), self.date)

        return hmac.new(self.apiSecretKey.encode('utf-8'),
                        auth_key.encode('utf-8'),
                        hashlib.md5).hexdigest()

    def execute(self, method, url):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Avangate-Authentication': "code='{}' date='{}' hash='{}'".format(self.merchantCode, \
                                                                                self.date, \
                                                                                self.__create_hash()),
        }

        return requests.request(method,
                                "{}{}".format(self.baseUrl, url), \
                                headers=headers)
