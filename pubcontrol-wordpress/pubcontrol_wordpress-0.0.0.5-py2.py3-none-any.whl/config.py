import os
from pubcontrol.config import Config as PubcontrolConfig

import pathlib


NAME = 'wordpress'

config_base = PubcontrolConfig().derive(NAME)


class Config(config_base):
    """
    CHANGELOG

    Changed 17.04.2018
    The PATH is now actually a pathlib Path and not a string.
    Added the TEMPLATE_PATH, which is the Path object to the templates folder
    """
    NAME = NAME
    PATH = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
    TEMPLATE_PATH = PATH / 'templates'
