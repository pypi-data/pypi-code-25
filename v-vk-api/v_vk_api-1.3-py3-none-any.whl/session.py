import json

import requests

from v_vk_api.exceptions import VVKAuthException
from v_vk_api.utils import \
    get_base_url, get_url_params, check_page_for_warnings


class APISession(requests.Session):
    """
    VK session with external proxy
    """
    LOGIN_URL = 'https://m.vk.com'
    METHOD_URL = 'https://api.vk.com/method'
    CAPTCHA_URI = 'https://api.vk.com/captcha.php'
    OAUTH_URL = 'https://oauth.vk.com/authorize'
    API_VERSION = '5.74'

    CAPTCHA_INPUT_PROMPT = 'Please enter characters from the image: {}\n'
    TWO_FACTOR_PROMPT = 'Please input characters, that you received ' \
                        'from two your factor authenticator:\n'
    PHONE_PROMPT = 'Please enter your phone number to confirm:\n'

    def __init__(self, app_id: int = None,
                 login: str = None,
                 password: str = None,
                 service_token: str = None,
                 proxies: dict = None):
        super().__init__()
        self.proxies = proxies
        self._app_id = app_id
        self._login = login
        self._password = password
        self._service_token = service_token
        self._access_token = self.get_access_token()

    def handle_captcha(self, query_params: dict,
                       html: str,
                       login_data: dict) -> requests.Response:
        """
        Handling CAPTCHA request
        """
        check_url = get_base_url(html)
        captcha_url = '{}?s={}&sid={}'.format(self.CAPTCHA_URI,
                                              query_params['s'],
                                              query_params['sid'])
        login_data['captcha_sid'] = query_params['sid']
        login_data['captcha_key'] = input(self.CAPTCHA_INPUT_PROMPT
                                          .format(captcha_url))
        return self.post(check_url, login_data)

    def handle_two_factor_check(self, html: str) -> requests.Response:
        """
        Handling two factor authorization request
        """
        action_url = get_base_url(html)
        code = input(self.TWO_FACTOR_PROMPT).strip()
        data = {'code': code, '_ajax': '1', 'remember': '1'}
        post_url = '/'.join((self.LOGIN_URL, action_url))
        return self.post(post_url, data)

    def handle_phone_number_check(self, html: str) -> requests.Response:
        """
        Handling phone number request
        """
        action_url = get_base_url(html)
        phone_number = input(self.PHONE_PROMPT)
        url_params = get_url_params(action_url)
        data = {'code': phone_number,
                'act': 'security_check',
                'hash': url_params['hash']}
        post_url = '/'.join((self.LOGIN_URL, action_url))
        return self.post(post_url, data)

    def check_for_additional_actions(self, url_params: dict,
                                     html: str,
                                     login_data: dict) -> None:
        """
        Checks the url for a request for additional actions,
        if so, calls the event handler
        """
        action_response = ''
        if 'sid' in url_params:
            action_response = self.handle_captcha(url_params, html, login_data)
        elif 'authcheck' in url_params:
            action_response = self.handle_two_factor_check(html)
        elif 'security_check' in url_params:
            action_response = self.handle_phone_number_check(html)
        if action_response:
            check_page_for_warnings(action_response.text)

    def login(self) -> bool:
        """
        Authorizes a user and returns a bool value of the result
        """
        response = self.get(self.LOGIN_URL)
        login_url = get_base_url(response.text)
        login_data = {'email': self._login, 'pass': self._password}
        login_response = self.post(login_url, login_data)
        url_params = get_url_params(login_response.url)
        self.check_for_additional_actions(url_params,
                                          login_response.text,
                                          login_data)
        if 'remixsid' in self.cookies or 'remixsid6' in self.cookies:
            return True

    def auth_oauth2(self) -> dict:
        """
        Authorizes a user by OAuth2 to get access token
        """
        oauth_data = {
            'client_id': self._app_id,
            'display': 'mobile',
            'response_type': 'token',
            'scope': '+66560',
            'v': self.API_VERSION
        }
        response = self.post(self.OAUTH_URL, oauth_data)
        url_params = get_url_params(response.url, fragment=True)
        if 'access_token' in url_params:
            return url_params

        action_url = get_base_url(response.text)
        if action_url:
            response = self.get(action_url)
            return get_url_params(response.url)

        response_json = response.json()
        if 'error' in response_json['error']:
            exception_msg = '{}: {}'.format(response_json['error'],
                                            response_json['error_description'])
            raise VVKAuthException(exception_msg)

    def get_access_token(self) -> str:
        """
        Returns the access token in case of successful authorization
        """
        if self._service_token:
            return self._service_token
        if self._app_id and self._login and self._password:
            try:
                if self.login():
                    url_params = self.auth_oauth2()
                    if 'access_token' in url_params:
                        return url_params['access_token']
            finally:
                self.close()  # close session because we do not need it more

    def send_method_request(self, method: str, method_params: dict) -> dict:
        """
        Sends user-defined method and method params
        """
        url = '/'.join((self.METHOD_URL, method))
        method_params['v'] = self.API_VERSION
        if self._access_token:
            method_params['access_token'] = self._access_token
        response = self.post(url, method_params, timeout=10)
        response.raise_for_status()
        return json.loads(response.text)
