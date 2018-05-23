# -*- coding: utf-8 -*-

"""Functions for getting the latest resources."""

from .utils import get_arty_annotation_module, get_arty_knowledge_module, get_arty_namespace_module, get_path_helper

__all__ = [
    'get_namespace_latest',
    'get_annotation_latest',
    'get_knowledge_latest',
]


def _get_latest_arty_helper(module_name, getter):
    """Help get the latest path for a given BEL module by paremetrizing the getter."""
    path = get_path_helper(module_name, getter)
    mp = max(path)
    return mp.as_posix()


def get_namespace_latest(module_name):
    """Get the latest path for this BEL namespace module.

    For historical reasons, some of these are not the same as the keyword. For example, the module name for HGNC is
    ``hgnc-human-genes`` due to the Selventa nomenclature.
    See https://arty.scai.fraunhofer.de/artifactory/bel/namespace/ for the entire manifest of available namespaces.

    :param str module_name: The BEL namespace module name
    :return: The URL of the latest version of this namespace
    :rtype: str
    """
    return _get_latest_arty_helper(module_name, get_arty_namespace_module)


def get_annotation_latest(module_name):
    """Get the latest path for this BEL annotation module.

    :param str module_name: The BEL annotation module name
    :return: The URL of the latest version of this annotation
    :rtype: str
    """
    return _get_latest_arty_helper(module_name, get_arty_annotation_module)


def get_knowledge_latest(module_name):
    """Get the latest path for this BEL annotation module.

    :param str module_name: The BEL knowledge module name
    :return: The URL of the latest version of this knowledge document
    :rtype: str
    """
    return _get_latest_arty_helper(module_name, get_arty_knowledge_module)
