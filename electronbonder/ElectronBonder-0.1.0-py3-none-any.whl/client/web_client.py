from requests import Session
from urllib.parse import urljoin, quote
import json


class ElectronBondAuthError(Exception): pass


def http_meth_factory(meth):
    '''Utility method for producing HTTP proxy methods for ElectronBondProxyMethods mixin class.

    Urls are prefixed with the baseurl defined
    '''
    def http_method(self, url, *args, **kwargs):
        full_url = urljoin(self.config['baseurl'], url)
        result = getattr(self.session, meth)(full_url, *args, **kwargs)
        return result
    return http_method


class ElectronBondProxyMethods(type):
    '''Metaclass to set up proxy methods for all requests-supported HTTP methods'''
    def __init__(cls, name, parents, dct):

        for meth in ('get', 'post', 'head', 'put', 'delete', 'options',):
            fn = http_meth_factory(meth)
            fn.__name__ = meth
            fn.__doc__ = '''Proxied :meth:`requests.Session.{}` method from :class:`requests.Session`'''.format(meth)

            setattr(cls, meth, fn)


class ElectronBond(metaclass=ElectronBondProxyMethods):
    '''ElectronBonder Web Client'''

    def __init__(self, **config):
        self.config = {}
        self.config.update(config)

        if not hasattr(self, 'session'): self.session = Session()
        self.session.headers.update({'Accept': 'application/json',
                                     'User-Agent': 'ElectronBond/0.1'})

    def authorize(self, username=None, password=None):
        '''Authorizes the client against the configured application instance.

        Parses the JSON response, and stores the returned session token in the authorization header for future requests.'''

        username = username or self.config['username']
        password = password or self.config['password']

        resp = self.session.post(
            urljoin(self.config['baseurl'], 'get-token/'),
            data={"password": password, "username": username}
        )

        if resp.status_code != 200:
            raise ElectronBondAuthError("Failed to authorize ElectronBond with status: {}".format(resp.status_code))
        else:
            session_token = json.loads(resp.text)['token']
            self.session.headers['Authorization'] = 'JWT {}'.format(session_token)
            return session_token
