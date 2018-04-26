import requests
from .const import KEYCLOAK_OPENID


class Auth(object):
    def __init__(self, ipaddr='127.0.0.1', port=8080, method='openid',
                 username='admin', password='admin', grant_type='password',
                 client_id='admin-cli', realm_name='master'):
        self.ipaddr = ipaddr
        self.port = port
        self.method = method
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.client_id = client_id
        self.realm_name = realm_name

    def openid_token(self):
        BASE_URL = '{}:{}{}'.format(self.ipaddr, self.port, '/auth')
        dict_args = {"realm_name": self.realm_name}
        URL = 'http://' + BASE_URL + KEYCLOAK_OPENID.format(**dict_args)
        payload = {
            "grant_type": self.grant_type,
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id
            }
        r = requests.post(URL, data=payload)
        try:
            # r = requests.post(URL, data=payload)
            return r.json()['access_token']
        except:
            r.raise_for_status()

    def args_parser(self, args):
        url_tail = ''
        for i in args:
            if args[i] is not None and i != 'self':
                url_tail += i+'='+str(args[i])+'&'
        return '?'+url_tail[:-1]
