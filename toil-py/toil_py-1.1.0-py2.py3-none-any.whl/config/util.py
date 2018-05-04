# -*- coding: utf-8 -*-
""" Handle onfigureation data. """
import logging
import codecs
import pkg_resources
import os
import errno

logger = logging.getLogger(__name__)

COMMON_CONFIG_ITEMS = ["alias", "log_level", "provider", "proxy"]


def load_default_config():
    """
    Load a default config file
    Returns: str
    """
    config_json = pkg_resources.resource_string(__name__, "config.json")
    return config_json


def generate_config_file(file_name=None):
    """
    Generate a new config file
    Args:
      file_name ():

    Returns: str
    """

    config_json = load_default_config()

    if file_name is not None:
        logger.info('config file:{file_name}'.format(file_name=file_name))
        if not os.path.exists(os.path.dirname(file_name)):
            try:
                os.makedirs(os.path.dirname(file_name))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with codecs.open(file_name, 'w', 'utf-8') as f:
            f.write(config_json)
            f.write('\n')
    else:
        print config_json

    return config_json
