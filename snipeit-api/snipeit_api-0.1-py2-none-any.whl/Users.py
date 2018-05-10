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

class Users(object):
    def __init__(self, server, token):
        self.server = server
        self.token = token

    def get(self, limit=None):
        if limit is not None:
            self.uri = '/api/v1/users?limit=' + str(limit)
        else:
            self.uri = '/api/v1/users'
            self.server = self.server + self.uri
        headers = {'Authorization': 'Bearer ' + self.token}
        results = requests.get(self.server, headers=headers)
        return results.content

    def create(self, payload):
        self.uri = '/api/v1/users'
        self.server = self.server + self.uri
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.post(self.server, headers=headers, data=payload)
        return json.dumps(results.json(),indent=4, separators=(',', ':'))

    def getID(self, user_name):
        self.uri = '/api/v1/users?search='
        self.server = self.server + self.uri + user_name
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.get(self.server, headers=headers)
        jsonData = json.loads(results.content)
        if len(jsonData['rows']) < 2 and jsonData['rows'][0]['id'] is not None:
            UserID = jsonData['rows'][0]['id']
        return UserID

    def updateUser(self, UserID, payload):
        self.uri = '/api/v1/users/'
        self.server = self.server + self.uri + UserID
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.patch(self.server, headers=headers, data=payload)
        jsonData = json.loads(results.content)
        return jsonData['status']

    def delete(self, UserID):
        self.uri = '/api/v1/users/'
        self.server = self.server + self.uri + UserID
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.delete(self.server, headers=headers)
        jsonData = json.loads(results.content)
        return jsonData['status']

    def getCheckedOutAssets(self, UserID):
        self.uri = '/api/v1/users/'
        self.server = self.server + self.uri + UserID + '/assets'
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + self.token}
        results = requests.get(self.server, headers=headers)
        return results.content
    
