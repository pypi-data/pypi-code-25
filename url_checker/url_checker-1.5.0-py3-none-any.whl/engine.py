import logbook
import requests
from requests.exceptions import ConnectionError, InvalidURL, MissingSchema


def get_status_code(url: str, should_format: bool = False) -> int:
    """
    Will make a get request to the provided url and return the response code.

    :param url: The URL to test as str.
    :param should_format: Whether to format the URL before the GET request as
    bool.
    :return: Status code of returned response as int

    EXAMPLE:
    >>> from url_checker.engine import get_status_code
    >>> get_status_code('https://www.yahoo.com/sports')
    200
    >>> get_status_code('http://arstechnica.com/not_real')
    404
    >>> get_status_code('google.com') # Will fail without protocol provided
    0
    >>> get_status_code('google.com', should_format=True)
    301
    """

    try:
        if should_format:
            url = format_url(url)
        status_code = requests.get(url, allow_redirects=False).status_code
        logbook.debug(f"{status_code} @ '{url}'")
        return status_code
    except (InvalidURL, MissingSchema):
        logbook.error(f"Invalid URL @ '{url}'")
        return 0
    except ConnectionError:
        logbook.error(f"Failed to establish a connection @ '{url}'")
        return 0


def format_url(url: str = None, force_https: bool = False) -> str:
    """
    Take URL which may or may-not be formatted and return a formatted one.

    :param url: URL to format as str.
    :param force_https: Whether to force return HTTPS URL as bool
    :return: Formatted URL as str.

    EXAMPLE:
    >>> from url_checker.engine import format_url
    >>> format_url('http://yahoo.com')
    'http://www.yahoo.com'
    >>> format_url('yahoo.com')
    'http://www.yahoo.com'
    >>> format_url('www.yahoo.com')
    'http://www.yahoo.com'
    >>> format_url('http://www.yahoo.com', force_https=True)
    'https://www.yahoo.com'
    """

    if url.startswith('http://') or url.startswith('https://'):
        formatted = url
    else:
        formatted = 'http://' + url
    if force_https:
        formatted = formatted.replace('http://', 'https://')

    return formatted
