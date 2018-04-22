
import requests
import logging

_LOGGER = logging.getLogger(__name__)

headers = {
    'Content-Type': 'application/json'
}


class FoobarRemote:

    def __init__(self, host, port=8888, username=None, password=None, timeout=5):

        self.host = host
        self.port = port
        if self.host is None:
            raise ValueError("FoobarRemote initialization failed: missing host")

        self.username = username
        if username is not None:
            _LOGGER.debug("Got username, will grab password and enable authentication")
            self.password = password
            self.auth = "{}:{}@".format(self.username, self.password)
        else:
            _LOGGER.debug("Username not found, Proceeding with authentication disabled")
            self.auth = ''

        self.http_schema = 'http'
        self.url = '{}://{}{}:{}/pyfoobar2k'.format(self.http_schema, self.auth, self.host, self.port)
        self.timeout = timeout

    def state(self):
        """Return info from player."""
        _LOGGER.debug("Fetching player info")
        parameters = {
            'cmd': None,
            'param3': 'state.json'
        }
        try:
            res = requests.get(url=self.url, headers=headers, params=parameters, timeout=self.timeout).json()
        except Exception as e:
            _LOGGER.error("Fetching player state failed with an Exception: %s", e)
            res = 'fetchStateFailed'
        return res

    def cmd(self, command, parameter=None):
        """Send command to player."""
        res = None
        _LOGGER.debug("Sending command %s to player with parameter %s", command, parameter)
        parameters = {
            'cmd': command,
            'param1': parameter
        }
        try:
            res = requests.get(url=self.url, headers=headers, params=parameters,
                               timeout=self.timeout).status_code
        except Exception as e:
            _LOGGER.error("Sending command to player failed with an Unknown Exception: %s", e)
        if res != 200:
            _LOGGER.error("Sending command to player failed, response status code: %s", res)
        return res

    def url(self):
        """.Return base url of player."""
        url = self.url
        return url

    def playlist(self):
        """.Return playlist info from player."""
        _LOGGER.debug("Fetching Playlist info")
        parameters = {
            'cmd': None,
            'param3': 'playlist.json'
        }
        try:
            res = requests.get(url=self.url, headers=headers, params=parameters, timeout=self.timeout).json()
        except requests.ConnectTimeout as t:
            _LOGGER.error("Fetching playlist info failed on Timeout Exception: %s", t)
            res = 'ConnectTimeout'
        except Exception as e:
            _LOGGER.error("Fetching playlist info failed with an Exception: %s", e)
            res = 'UnknownError'
        return res
