from urllib.parse import urlparse, parse_qsl

from bs4 import BeautifulSoup

from v_vk_api.exceptions import VVKPageWarningException, VVKBaseUrlException


def get_base_url(html: str) -> str:
    """
    Search for login url from VK login page
    """
    forms = BeautifulSoup(html, 'html.parser').find_all('form')
    if not forms:
        raise VVKBaseUrlException('Form for login not found')
    elif len(forms) > 1:
        raise VVKBaseUrlException('More than one login form found')
    login_url = forms[0].get('action')
    if not login_url:
        raise VVKBaseUrlException('No action tag in form')
    return login_url


def get_url_params(url: str, fragment: bool = False) -> dict:
    """
    Parse URL params
    """
    parsed_url = urlparse(url)
    if fragment:
        url_query = parse_qsl(parsed_url.fragment)
    else:
        url_query = parse_qsl(parsed_url.query)
    return dict(url_query)


def check_page_for_warnings(html: str) -> None:
    """
    Checks if is any warnings on page if so raises an exception
    """
    soup = BeautifulSoup(html, 'html.parser')
    warnings = soup.find_all('div', {'class': 'service_msg_warning'})
    if warnings:
        exception_msg = '; '.join((warning.get_text() for warning in warnings))
        raise VVKPageWarningException(exception_msg)
