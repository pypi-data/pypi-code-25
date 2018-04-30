from typing import Union

from v_vk_api.session import APISession
from v_vk_api.exceptions import VVKApiException


class API:
    """
    VK API wrapper
    """
    def __init__(self, session: APISession) -> None:
        self.session = session

    def request_method(self, method: str,
                       **method_kwargs: Union[str, int]) -> dict:
        """
        Process method request and return json with results

        :param method: str: specifies the method, example: "users.get"
        :param method_kwargs: dict: method parameters,
        example: "users_id=1", "fields='city, contacts'"
        """
        response = self.session.send_method_request(method, method_kwargs)
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

        return response
