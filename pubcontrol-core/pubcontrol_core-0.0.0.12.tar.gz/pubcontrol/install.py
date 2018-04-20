from pubcontrol.plugin import hookspec, hookimpl, PluginManager, PluginLoader
from pubcontrol.config import Config

import os
import pathlib
import optparse
import importlib

from jutil.installation import yesno_prompt, folder_prompt

import jinja2
from pubcontrol.hook import *


PATH = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
TEMPLATE_PATH = PATH / 'templates' / 'ini'
TEMPLATE_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATE_PATH)))


def install_config(
        folder_path,
        mysql_host='localhost',
        mysql_database='pubcontrol',
        mysql_username='',
        mysql_password='',
        file_name='config.ini',
        template_name='config.j2'
):
    file_path = folder_path / file_name
    template_path = TEMPLATE_PATH / template_name
    print('[Config] The template path "{}" exists: {}'.format(str(template_path), template_path.exists()))
    print('[Config] Installing the "{}" in "{}"'.format(template_name, file_path))
    template = TEMPLATE_ENV.get_template(template_name)
    content = template.render(
        mysql_host=mysql_host,
        mysql_database=mysql_database,
        mysql_username=mysql_username,
        mysql_password=mysql_password
    )
    with file_path.open(mode='w+') as file:
        file.write(content)
        print('[Config] "{}" written'.format(file_name))


def write_project_path(folder_path):
    module_path = PATH / 'config.py'
    print('[Config] Hard-coding the project path into config module at "{}"'.format(str(module_path)))
    with module_path.open(mode='r') as file:
        lines = file.readlines()
        print('[Config] {} lines in config'.format(len(lines)))
    with module_path.open(mode='w') as file:
        for i in range(len(lines)):
            line = lines[i]
            # print('[Config][Line] {}'.format(line))
            if 'PROJECT_PATH' in line:
                print('[Config] observed "{}"'.format(line))
                lines[i] = 'PROJECT_PATH = pathlib.Path("{}")'.format(str(folder_path))
                print('[Config] replaced with "{}"'.format(lines[i]))
                break
        file.writelines(lines)
        print('[Config] {} lines written back to module')


def create_all():
    from pubcontrol.database import MySQLDatabase
    from pubcontrol.register import BASE

    print('[Database] Attempting to load all the additional models from the plugins')
    module_names = PluginManager().hook.register_models()
    for module_name in module_names:
        print('[Database] importing from "{}"'.format(module_name))
        importlib.import_module(module_name)
    MySQLDatabase().create_all(BASE)


def install_all():
    path = folder_prompt(
        'Please choose a project path for PUBCONTROL. All the configuration files will be installed there',
        suggest_cwd=True,
        mkdir=True
    )
    print('[install] chosen path "{}"'.format(str(path)))
    # Installing the config file
    install_config(
        path,
        mysql_username='root',
        mysql_password='struppi98'
    )
    # Hardcoding the project path into the config.py
    write_project_path(path)
    # Attempting to make the database
    create_all()
    # Calling the installs of the plugins
    plugin_loader = PluginLoader()
    plugin_loader.load()
    plugin_manager = PluginManager()
    for install_return in plugin_manager.hook.install():
        print(install_return)


if __name__ == '__main__':
    install_all()
