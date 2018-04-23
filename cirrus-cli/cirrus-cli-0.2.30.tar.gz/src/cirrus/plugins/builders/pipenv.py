#!/usr/bin/env python
"""
pipenv

"""
import os

from cirrus.builder_plugin import Builder
from cirrus.logger import get_logger
from cirrus.invoke_helpers import local
from cirrus.pypirc import build_pip_command


LOGGER = get_logger()


class Pipenv(Builder):
    """
    Builder Plugin that uses VirtualEnv and Pip to
    create a development environment and install dependencies

    """
    def __init__(self):
        super(Pipenv, self).__init__()



    def create(self, **kwargs):
        """
        build the virtualenv
        """

    def clean(self, **kwargs):
        if os.path.exists(self.venv_path):
            cmd = "rm -rf {0}".format(self.venv_path)
            LOGGER.info("Removing virtualenv: {0}".format(self.venv_path))
            local(cmd)

    def activate(self):
        command = ". {}/bin/activate".format(self.venv_path)
        return command