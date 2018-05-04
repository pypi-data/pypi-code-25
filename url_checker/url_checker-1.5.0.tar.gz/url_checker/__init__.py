"""
format_url:
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


get_status_code:
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

__version__ = "1.5.0"
