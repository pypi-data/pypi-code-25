"""
Backlog Client object
"""

import os
import json
import requests

from .resourse import *
from .utilities import save_image_file


class BacklogClient:
    """Backlog API"""

    def __init__(self, api_key, space_name):
        """
        Backlog api client
        :param str api_key: API key
        :param str space_name: Backlog space
        """
        self._api_key = api_key
        self._space_name = space_name
        self.model_endpoint = f'https://{self._space_name}.backlog.jp/api/v2/'
        self.role = None
        self.space = Space(self)
        self.user = User(self)
        self.group = Group(self)
        self.project = Project(self)
        self.issue = Issue(self)
        self.webhook = Webhook(self)
        self.notification = Notification(self)
        self.repository = Repository(self)
        self.pullrequest = PullRequest(self)
        self.wiki = Wiki(self)

    def fetch_json(self, uri_path, method='GET', headers=None, query_params=None, post_params=None, files=None):
        """
        Making request by this function arguments
        :param str uri_path: uri path continue endpoint
        :param str method: request method
        :param str headers: request headers
        :param dict query_params: query parameter
        :param dict post_params: base of data
        :param files:
        """
        if headers is None:
            headers = {}
        if query_params is None:
            query_params = {}
        if post_params is None:
            post_params = {}
        query_params['apiKey'] = self._api_key

        data = None
        if files is None:
            data = json.dumps(post_params)

        if method.upper() in ('POST', 'PUT', 'DELETE') and files is not None:
            headers['Content-Type'] = 'application/json; charset=utf8'
        headers['Accept'] = 'application/json'

        if uri_path.startswith('/'):
            uri_path = uri_path[1:]
        url = self.model_endpoint + uri_path

        response = requests.request(method=method, url=url, params=query_params, headers=headers,
                                    data=data, files=files)

        if response.status_code >= 400:
            raise Exception(response, response.text)
        elif response.status_code == 204:
            return None

        if response.headers['Content-Type'] == 'image/png':
            ext = response.headers['Content-Type'].split('/')[1]
            save_image_file('space_img', ext, response.content)
            return None
        return response.json()

    def check_role(self):
        """
        Check client user authority
        """
        res = self.fetch_json('users/myself')
        self.role = res.get('roleType', None)
