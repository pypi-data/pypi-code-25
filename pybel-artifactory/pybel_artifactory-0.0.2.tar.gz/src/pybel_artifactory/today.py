# -*- coding: utf-8 -*-

"""Functions for minting new URLs for BEL resources."""

import time

from .utils import get_arty_annotation, get_arty_knowledge, get_arty_namespace

__all__ = [
    'get_namespace_today',
    'get_annotation_today',
    'get_knowledge_today',
]


def get_iso_8601_date():
    """Get the current ISO 8601 date as a string.

    :rtype: str
    """
    return time.strftime('%Y%m%d')


def get_namespace_today(module_name):
    """Get the right name for the next version of the namespace.

    :param str module_name: The name of the namespace resource
    :rtype: str
    """
    return get_arty_namespace(module_name, get_iso_8601_date())


def get_annotation_today(module_name):
    """Get the right name for the next version of the annotation.

    :param str module_name: The name of the annotation resource
    :rtype: str
    """
    return get_arty_annotation(module_name, get_iso_8601_date())


def get_knowledge_today(module_name):
    """Get the right name for the next version of the knowledge resource.

    :param str module_name: The name of the knowledge resource
    :rtype: str
    """
    return get_arty_knowledge(module_name, get_iso_8601_date())
