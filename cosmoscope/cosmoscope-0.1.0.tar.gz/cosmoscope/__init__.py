# -*- coding: utf-8 -*-

"""Top-level package for Cosmoscope."""

import logging
import os
import sys
import importlib.util as util

__author__ = """Nicholas Earl"""
__email__ = 'contact@nicholasearl.me'
__version__ = '0.1.0'

logging.basicConfig(format='cosmoscope [%(levelname)-8s]: %(message)s',
                    level=logging.INFO)


def load_user():
    """
    Imports any python files that exist in the user's `.cosmoscope` directory.
    """
    # Get the path relative to the user's home directory
    path = os.path.expanduser("~/.cosmoscope")

    # If the directory doesn't exist, create it
    if not os.path.exists(path):
        os.mkdir(path)

    # Import all python files from the directory
    for file in os.listdir(path):
        if not file.endswith("py"):
            continue

        spec = util.spec_from_file_location(file[:-3], os.path.join(path, file))
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)

load_user()
