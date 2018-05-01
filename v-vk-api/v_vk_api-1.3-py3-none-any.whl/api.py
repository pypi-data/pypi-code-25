from typing import Union

from v_vk_api.session import APISession
from v_vk_api.exceptions import VVKApiException


class API:
    """
    VK API wrapper
    """
    def __init__(self, session: APISession) -> None:
        self.session = session

    def check_for_errors(self, method, method_kwargs, response):
        if 'error' in response:
            api_error = VVKApiException(response['error'])
            if api_error.code == 14:  # captcha needed error
                captcha_key = input('Please enter characters from image: {}\n'
                                    .format(api_error.captcha_url))
                # user can just cancel CAPTCHA input and proceed with error
                if captcha_key:
                    method_kwargs['sid'] = api_error.captcha_sid
                    method_kwargs['key'] = captcha_key
                    return self.request_method(method, **method_kwargs)
            raise api_error

    def request_method(self, method: str,
                       **method_kwargs: Union[str, int]) -> dict:
        """
        Process method request and return json with results

        :param method: str: specifies the method, example: "users.get"
        :param method_kwargs: dict: method parameters,
        example: "users_id=1", "fields='city, contacts'"
        """
        response = self.session.send_method_request(method, method_kwargs)
        self.check_for_errors(method, method_kwargs, response)
        return response

    def request_get_user(self, user_ids) -> dict:
        """
        Method to get users by ID, do not need authorization
        """
        method_params = {'user_ids': user_ids}
        response = self.session.send_method_request('users.get', method_params)
        self.check_for_errors('users.get', method_params, response)
        return response

    def request_set_status(self, text: str) -> dict:
        """
        Method to set user status
        """
        method_params = {'text': text}
        response = self.session.send_method_request('status.set', method_params)
        self.check_for_errors('status.set', method_params, response)
        return response

    def request_clear_status(self) -> dict:
        """
        Method to clear user status
        """
        return self.request_set_status('')
