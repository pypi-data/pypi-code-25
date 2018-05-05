from typing import List

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest

__all__ = (
    'get_protocol',
    'get_domain',
    'to_list',
    'to_str',
)


def get_protocol() -> str:
    """
    Returns data transfer protocol name.
    The value is determined by bool variable 'USE_HTTPS' in settings.

    Returns:
        str: 'https' if 'USE_HTTPS' is True, otherwise - 'http'.
    """
    
    return 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'


def get_domain(request: WSGIRequest=None) -> str:
    """
    Returns domain name this site.

    Args:
        request (WSGIRequest): Request.

    Returns:
        str: Domain name.
    """
    site_name = cache.get('site_name')

    if site_name is None:
        site_name = Site.objects.get_current(request).domain
        ttl = getattr(settings, 'CACHES', {}).get('default', {}).get('TIMEOUT')
        cache.set('site_name', site_name, ttl)

    return site_name


def to_list(string: str) -> List[str]:
    """
    Transforms string to list.
    
    Args:
        string (str): String to transform.

    Returns:
        List[str]: List
    """
    
    return string.split(',')


def to_str(_list: List[str]) -> str:
    """
    Transforms list to str.
    
    Args:
        _list (List[str]): List to transform to str

    Returns:
        str: Transformed list
    """
    
    return ','.join(_list)
