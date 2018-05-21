# -*- coding: utf-8 -*-

"""
Main module.
"""

import os
import sys
from .util import click_funcs
from .util import shell_funcs

def run_conda_create(name):
    """
    The program's main routine.
    """
    # Defaults
    env_path = shell_funcs.get_default_conda_env_path()
    py_version = '3.6'
    libs = {'pylint': 'y',
            'requests': 'y'}

    env_path = click_funcs.click_prompt_custom_var('Path to environment',
                                                   "" if env_path == '0' else env_path)
    if not os.path.isdir(env_path):
        print(env_path + ' is not a valid path. Exiting.')
        sys.exit(1)

    py_version = click_funcs.click_prompt_custom_var('Python version', py_version)

    for key in libs.keys():
        tmp = click_funcs.click_prompt_yes_no('Install {}?'.format(key), default=libs.get(key))
        libs[key] = tmp

    # add options for kivy

    tmp_lst = [key for key in libs if libs[key] == True]
    cmd = 'conda create -y -q -p {} -c conda-forge python={} {}'
    shell_funcs.run_in_shell_without_output(cmd.format(os.path.join(env_path, name),
                                                       py_version,
                                                       " ".join(tmp_lst)))

    create_dirs = click_funcs.click_prompt_yes_no('Create de-/activate.d directories?', 'y')
    if create_dirs:
        shell_funcs.create_env_dirs(env_path, name)

    # print de-/activate-script directory
