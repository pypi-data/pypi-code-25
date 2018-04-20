import os

from jutil.configuration import config_singleton

from ScopusWp.config import PROJECT_PATH

from pubcontrol.config import Config as PubcontrolConfig

import pathlib

NAME = 'scopus'
DB_NAME = '__scopus'
PATH = os.path.dirname(os.path.realpath(__file__))


class Config(PubcontrolConfig().derive(NAME)):

    NAME = NAME
    PATH = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
