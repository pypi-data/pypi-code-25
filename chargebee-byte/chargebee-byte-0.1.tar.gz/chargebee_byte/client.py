import requests

from chargebee_byte.requests import SubscriptionRequest


class Client(object):
    def __init__(self, site, api_key):
        self.auth = requests.auth.HTTPBasicAuth(api_key, '')
        self.api_url = 'https://{}.chargebee.com/api/v2'.format(site)

    def get_subscriptions(self, parameters=None):
        request = SubscriptionRequest(parameters)
        response = requests.get(self.api_url + request.path, auth=self.auth, params=request.data)
        response.raise_for_status()
        return response.json()
