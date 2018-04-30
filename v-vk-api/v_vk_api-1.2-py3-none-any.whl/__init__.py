from v_vk_api.api import API
from v_vk_api.session import APISession

__author__ = 'vadimk2016'
__version__ = '1.0'
__email__ = 'vadim.kuznyetsov@gmail.com'


def create(app_id: int = None,
           login: str = None,
           password: str = None,
           service_token: str = None,
           proxies: dict = None) -> API:
    """
    Creates an API instance, requires app ID,
    login and password or service token to create connection

    :param app_id: int: specifies app ID
    :param login: str: specifies login, can be phone number or email
    :param password: str: specifies password
    :param service_token: str: specifies password service token
    :param proxies: dict: specifies proxies, require http and https proxy
    """
    session_ = APISession(app_id,
                          login,
                          password,
                          service_token,
                          proxies)
    return API(session_)
