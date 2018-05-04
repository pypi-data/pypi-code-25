from .const import KEYCLOAK_USER, KEYCLOAK_USER_ID, KEYCLOAK_REALMS, KEYCLOAK_USER_SESSION, KEYCLOAK_ATTACK_DETECTION, KEYCLOAK_SESSION, KEYCLOAK_RESET_PASSWORD
import requests
from .utils import Auth
import json


class Client(Auth):
    def userlist(self, email=None, first=None, firstName=None, lastName=None,
                 max=None, search=None, username=None):
        args = locals()
        url_tail = self.args_parser(args)
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token}
        URL = 'http://' + BASE_URL + KEYCLOAK_USER.format(**dict_args) + url_tail
        r = requests.get(URL, headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    # TODO
    # need get args like userlist
    def createuser(self, payload):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_USER.format(**dict_args)
        r = requests.post(URL, data=json.dumps(payload), headers=headers)
        try:
            if r.json() is not None:
                return r.json()
            return {"message": "create user success"}
        except:
            r.raise_for_status()

    def updateuser(self, userid, payload):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name, "id": userid}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_USER_ID.format(**dict_args)
        r = requests.put(URL, data=json.dumps(payload), headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    def usermessage(self, userid):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name, "id": userid}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_USER_ID.format(**dict_args)
        r = requests.get(URL, headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    def usersession(self, userid):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name, "id": userid}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_USER_SESSION.format(**dict_args)
        r = requests.get(URL, headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    def realmconfig(self):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_REALMS.format(**dict_args)
        r = requests.get(URL, headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    def putRealmConfig(self, payload):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_REALMS.format(**dict_args)
        r = requests.put(URL, headers=headers, data=json.dumps(payload))
        try:
            return r.json()
        except:
            r.raise_for_status()

    def userstates_attack(self, userid):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name, "id": userid}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_ATTACK_DETECTION.format(**dict_args)
        r = requests.get(URL, headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    # user sessions
    def logoutsession(self, sessionid):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name, "sessionid": sessionid}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_SESSION.format(**dict_args)
        r = requests.delete(URL, headers=headers)
        try:
            return r.json()
        except:
            r.raise_for_status()

    def reset_password(self, userid, payload):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name, "id": userid}
        openid_token = 'Bearer ' + self.openid_token()
        headers = {'Authorization': openid_token, 'Content-Type': 'application/json'}
        URL = 'http://' + BASE_URL + KEYCLOAK_RESET_PASSWORD.format(**dict_args)
        r = requests.put(URL, headers=headers, data=json.dumps(payload))
        try:
            return r.json()
        except:
            r.raise_for_status()
