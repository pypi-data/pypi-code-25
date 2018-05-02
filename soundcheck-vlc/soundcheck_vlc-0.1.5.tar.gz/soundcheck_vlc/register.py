#!/usr/bin/env python3
"""
    source: https://framagit.org/bortzmeyer/mastodon-DNS-bot/blob/master/register.py
"""


import getpass

from mastodon import Mastodon

from .utils.config import MY_APP_NAME, app_cred_file_path, app_user_data_dir, user_cred_file_path, get_config_or_create
from os.path import isfile, exists
from os import makedirs


# Register app - only once!
def register_app(config):
    """
    Register a new mastodon app if the credential file doesn't exists
    :param config: app config dict
    :type config: dict
    :return: Boolean value: True if the app was previously registered, False otherwise
    :rtype: bool
    """
    is_reg = isfile(app_cred_file_path)
    if not is_reg:
        if not exists(app_user_data_dir):
            makedirs(app_user_data_dir)

        Mastodon.create_app(
            MY_APP_NAME,
            scopes=['read'],
            api_base_url=config['mastodon']['instance'],
            to_file=app_cred_file_path
        )
    return is_reg


def login_user(config):
    """
    Login the declared user.
    If the credential file doesn't exists yet, the user is prompted for a password and
    a new credential file is generated.
    :param config:
    :return: A boolean set to true if the user credential file previously existed
    """
    is_reg = isfile(user_cred_file_path)
    if not is_reg:
        mastodon = Mastodon(
            client_id = app_cred_file_path,
            api_base_url = config['mastodon']['instance']
        )

        p = getpass.getpass(prompt='Enter your mastodon account password:')

        mastodon.log_in(
            config['mastodon']['user'],
            p,
            scopes=['read'],
            to_file=user_cred_file_path
        )
    return is_reg


def init_instance(config):
    """
    :param config:
    :return: A mastodon object
    :rtype: Mastodon
    """
    # config = get_config_or_create()

    register_app(config)
    login_user(config)

    mastodon = Mastodon(
        client_id = app_cred_file_path,
        access_token=user_cred_file_path ,
        api_base_url = config['mastodon']['instance'],
        # mastodon_version='2.3.3'  # Mastodon.py seems unable to fetch the version from mastodon.xyz
    )

    return mastodon

