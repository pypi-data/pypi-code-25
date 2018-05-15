import os
import re
import sys

import click


def get_path(name):
    name = name.lower()
    name = '.{}'.format(name)

    paths = []
    for path in os.listdir(os.path.expanduser('~')):
        path = os.path.join(os.path.expanduser('~'), path)
        if os.path.isdir(path):
            folder = os.path.basename(path)
            folder = folder.lower()
            if folder.startswith(name):
                paths.append(path)

    if len(paths) == 0:
        click.echo('No paths matching {} found!'.format(name))
        sys.exit(0)
    elif len(paths) > 1:
        click.echo('More than one path matching {} found!'.format(name))
        sys.exit(0)
    else:
        return paths[0]


home = os.path.expanduser('~')

jetbrains_folders = []
for item in os.listdir(home):
    path = os.path.join(home, item)
    if not os.path.isdir(path):
        continue

    folders = os.listdir(path)
    if len(folders) != 2:
        continue

    if 'config' not in folders or 'system' not in folders:
        continue

    jetbrains_folders.append(item)

options = [re.match(r'\.([A-Za-z]+)[0-9.]+', folder).group(1).lower() for folder in jetbrains_folders]

del home
del jetbrains_folders
