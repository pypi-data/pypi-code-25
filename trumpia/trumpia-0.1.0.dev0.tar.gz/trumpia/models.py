import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry


class TrumpiaListData(object):

    def __init__(self, **kwargs):
        self.mobile_count = None
        self.email_count = None,
        self.subscription_count = None
        self.description = None
        self.list_id = None
        self.list_name = None
        self.display_name = None
        self.frequency = None
        self.list_id = None
        for key, value in kwargs.iteritems():
            if 'count' in key or 'frequency' in key:
                setattr(self, key, int(value))
            else:
                setattr(self, key, value)


class TrumpiaList(object):

    def __init__(self, **kwargs):
        self.list_id = None
        self.list_name = None
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class TrumpiaAPI(object):
    """
    Object for interacting with Trumpia's API.
    So far it's mainly for getting data and not mutating and of Trumpia's API objects.
    For more Trumpia API features see: https://trumpia.com/api/docs/rest/overview.php
    """

    def __init__(self, config):
        self.username = config.get('Trumpia', 'username')
        self.api_key = config.get('Trumpia', 'api_key')
        self.content_type = 'application/json'
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({'X-Apikey': self.api_key, 'Content-Type': self.content_type})
            retries = Retry(total=5, backoff_factor=0.1)
            self._session.mount('http://', HTTPAdapter(max_retries=retries))
            return self._session
        else:
            return self._session

    @property
    def base_api_endpoint(self):
        return 'http://api.trumpia.com/rest/v1/%s' % self.username

    @property
    def lists_api_endpoint(self):
        return self.base_api_endpoint + '/list'

    # def get_lists(self) -> Iterator[TrumpiaList]:
    def get_lists(self):
        """
        Returns all the marketing lists in FlexShopper's Trumpia account as a list of TrumpiaList objects

        :return: Iterator[TrumpiaList]
        """
        response = self.session.get(
            self.lists_api_endpoint,
        )
        trumpia_lists = response.json()['list']
        for trumpia_list in trumpia_lists:
            yield TrumpiaList(**trumpia_list)

    # def get_list_data(self, trumpia_list: TrumpiaList) -> TrumpiaListData:
    def get_list_data(self, trumpia_list):
        """
        Returns the details of a list

        :param trumpia_list: TrumpiaList object

        :return TrumpiaListData: object that contains all list data
        """
        response = self.session.get(
            self.lists_api_endpoint + '/%s' % trumpia_list.list_id,
        )
        list_data = response.json()
        list_data['list_id'] = trumpia_list.list_id
        return TrumpiaListData(**list_data)
