import json
import shutil
from appdirs import AppDirs  # Lib used to locate the relevant user data folder based on the host OS
                             # (e.g. ~/.local/share)
from os.path import join, isfile, exists, realpath, dirname
from os import rename, makedirs

MY_APP_NAME = 'SoundCheckVLC'
app_user_data_dir = AppDirs(MY_APP_NAME, "alfajet").user_data_dir

config_file_name = 'soundcheck.config.json'
config_file_path = join(app_user_data_dir, config_file_name)

app_cred_file_name = MY_APP_NAME + "_clientcred.secret"
app_cred_file_path = join(app_user_data_dir, app_cred_file_name)

user_cred_file_name = MY_APP_NAME + "_usercred.secret"
user_cred_file_path = join(app_user_data_dir, user_cred_file_name)

logging_config_name = 'logging.conf'
logging_config_path = join(app_user_data_dir, logging_config_name)
logging_config_template = join(dirname(realpath(__file__)), logging_config_name)

def get_config_or_create():
    """
    Return config from config file as a dict.
    If the file is missing, a new one is created.
    :return: dict
    :rtype: dict
    """
    if isfile(config_file_path):
        with open(config_file_path, 'r') as f:
            return json.load(f)
    else:
        return set_config()


def save_config(config):
    """
    Serialise configuration in a json file.
    :param config:
    :return: None
    """
    if not exists(app_user_data_dir):
        makedirs(app_user_data_dir)
    if isfile(config_file_path):
        rename(config_file_path, join(app_user_data_dir, config_file_name + '.bak'))
    with open(config_file_path, 'w') as f:
        json.dump(config, f)


def get_config_tpl():
    """
    Create an empty configuration dict
    :return: config dict
    :rtype: dict
    """
    cfg = {
        'mastodon': {
            'instance': '',
            'user': '',
            'tag': 'soundcheck'
        },
        'vlc': {
            'port': '8080',
            'password': ''
        }
    }
    return cfg


def set_config():
    """
    Asks user to provide configuration values and save them.
    Returns the config dict
    :return: config dict
    :rtype: dict
    """
    config = get_config_tpl()
    for k, v in config.items():
        for l in v.keys():
            x = input(k + '.' + l + ': ')
            config[k][l] = x

    save_config(config)
    return config


def get_logger_config():
    """
    Get loggin file settings location.
    If the file is missing, then a new file is created from the template.
    :return: Logging file path
    """
    if not isfile(logging_config_path):
        shutil.copy(logging_config_template, logging_config_path)

    return logging_config_path


if __name__ == '__main__':
    print(get_logger_config())
