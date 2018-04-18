# -*- coding: utf8 -*-
"""
Define a setuptools extension.


Host usage::

    setup(
        ...,
        reentry_scan=['group1', 'group2'],
        ...
    )

Plugin usage::

    setup(
        ...,
        reentry_register = True,
        ...
    )
"""
from __future__ import print_function
from logging import getLogger

from reentry.config import get_datafile


def is_bool(value):
    """Return True if `value` is a boolean."""
    return bool(value) == value


def register_dist(dist, attr, value):
    """If value is True, register the distribution's entry points in reentrys storage."""
    from distutils.errors import DistutilsSetupError  # pylint: disable=import-error,no-name-in-module
    # assert is boolean
    logger = getLogger('pip')

    if not is_bool(value):
        raise DistutilsSetupError('{} must be a boolean, got {}'.format(attr, value))

    if value:
        logger.warning('registering entry points with reentry...')
        from reentry import manager
        # ~ print('\n'.join(['{} = {}'.format(k, v) for k, v in dist.__dict__.items()]))
        dist_name, entry_point_map = manager.register(dist)
        logger.warning('registered to %s', get_datafile())
        logger.info('Following entrypoints were registered\n %s', get_datafile())

        logger.info(manager.format_map({dist_name: entry_point_map}))


def ensure_list(value, attr):
    """raise an error if `value` is not a list"""
    from distutils.errors import DistutilsSetupError  # pylint: disable=import-error,no-name-in-module
    if not isinstance(value, list):
        raise DistutilsSetupError('{} must be a list, got {}'.format(attr, value.__class__))


def scan_for_installed(dist, attr, value):  # pylint: disable=unused-argument
    """
    scan for entry points of the given groups in the already installed
    distributions

    :param value: a list of groups names to scan for
    """
    logger = getLogger('pip')
    ensure_list(value, attr)
    if value:
        logger.warning('scanning for plugins...')
        from reentry import manager
        manager.scan(groups=value, group_re=False)
        logger.warning('... plugin scanning done.')
        logger.info('Current entry point map at %s:', get_datafile())
        logger.info(manager.format_map(manager.get_entry_map()))
