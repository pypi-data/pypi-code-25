import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
import requests
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass
else:
    requests.packages.urllib3.disable_warnings()
try:
    from .packages.urllib3.exceptions import ResponseError
except:
    pass

import json

class Consumables(object):
    def __init__(self, server, token):
        self.server = server
        self.token = token

    def get(self, limit=None):
        if limit is not None:
            self.uri = '/api/v1/consumables?limit=' + str(limit)
        else:
            self.uri = '/api/v1/consumables'
        self.server = self.server + self.uri
        headers = {'Authorization': 'Bearer ' + self.token}
        results = requests.get(self.server, headers=headers)
        return results.content

    def create(self, payload):
        self.uri = '/api/v1/consumables'
        self.server = self.server + self.uri
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.post(self.server, headers=headers, data=payload)
        return json.dumps(results.json(),indent=4, separators=(',', ':'))

    def getID(self, asset_name):
        self.uri = '/api/v1/consumables?search='
        self.server = self.server + self.uri + asset_name
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.get(self.server, headers=headers)
        jsonData = json.loads(results.content)
        if len(jsonData['rows']) < 2 and jsonData['rows'][0]['id'] is not None:
            ConsumableID = jsonData['rows'][0]['id']
        return ConsumableID

    def viewID(self, ConsumableID):
        self.uri = '/api/v1/consumables/'
        self.server = self.server + self.uri + ConsumableID
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.get(self.server, headers=headers)
        return results.content
