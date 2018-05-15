import os
import re
import subprocess
import tarfile

import click
import elevate

from oversee import config


def install(name):
    click.echo('Installing {}'.format(name))
    commands = config.install[name]
    for command in commands:
        interpret(command, name)


def interpret(command, name):
        if isinstance(command, dict):
            for key in command:
                if isinstance(command[key], list):
                    for item in command[key]:
                        COMMANDS[key](item)
                else:
                    COMMANDS[key](command[key])
        else:
            try:
                COMMANDS[command](name)
            except KeyError:
                run(command)


def run(command, background=False):
    commands = command.split('|')

    stdin = None
    for command in commands:
        command = command.split()
        if background:
            process = subprocess.Popen(command, stdin=stdin)
        else:
            process = subprocess.Popen(command, stdin=stdin)
            process.wait()
        stdin = process.stdout


def add_apt_repository(repo):
    run('sudo add-apt-repository {}'.format(repo))


def apt_get(item):
    run('sudo apt-get update')
    run('sudo apt-get install {}'.format(item))


def jetbrains(code):
    url = 'https://data.services.jetbrains.com/products/download?code={}&platform=linux'.format(code)
    root = os.path.dirname(__file__)
    tar_filename = '{}.tar.gz'.format(code)

    src = os.path.join(root, '.temp', tar_filename)
    dst = os.path.join(os.path.expanduser('~'), 'Applications')

    elevate.file.download(url, src)

    os.makedirs(dst, exist_ok=True)
    tar = tarfile.open(src, 'r:gz')
    tar.extractall(dst)

    folder = os.path.commonprefix(tar.getnames())
    folder = folder.lower()

    tar.close()
    os.remove(src)

    if not folder:
        raise ValueError('No common prefix found within {}. Extracted files remain in {}!'.format(src, dst))

    application, _ = folder.split('-')
    run(os.path.join(dst, folder, 'bin', '{}.sh'.format(application)), background=True)


COMMANDS = {'apt-get': apt_get, 'install': install, 'repository': add_apt_repository, 'jetbrains': jetbrains}


def export_aliases(name):
    aliases = config.get_aliases(name)
    if aliases is None:
        click.echo('{} aliases do not exist in .oversee.yaml'.format(name))

    inherit = aliases.get('inherit', [])
    if isinstance(inherit, str):
        inherit = [inherit]

    for parent in inherit:
        aliases = elevate.builtin.dict_merge(config.get_aliases(parent), aliases)

    bash_aliases = ''
    for alias, command in aliases.get('aliases', {}).items():
        bash_aliases += 'alias {}="{}"\n'.format(alias, command)

    bash_aliases += '\n'
    for link in aliases.get('links', []):
        bash_aliases += 'sudo ln -sf {} {}\n'.format(link['that'], link['this'])

    bash_aliases += '\n'
    for name, lines in aliases.get('functions', {}).items():
        bash_aliases += '{}()'.format(name)
        bash_aliases += ' {\n'
        for line in lines:
            bash_aliases += '    {}\n'.format(line)
    bash_aliases += '}\n'

    bash_aliases += '\n'
    for name, export in aliases.get('exports', {}).items():
        export = os.path.expanduser(export)
        export = export.rstrip('\n')
        bash_aliases += 'export {}="{}"\n'.format(name, export)

    bash_aliases += '\n'
    for path in aliases.get('keys', []):
        path = os.path.expanduser(path)
        bash_aliases += 'ssh-add {}\n'.format(path)

    bash_aliases += '\n'
    for source in aliases.get('sources', []):
        source = os.path.expanduser(source)

        if not os.path.exists(source):
            click.echo('{} does not exist. Skipping source!'.format(source))
            continue

        bash_aliases += 'source {}\n'.format(source)

    bash_aliases += '\n'
    for eval in aliases.get('eval', []):
        bash_aliases += 'eval "{}"'.format(eval)

    path = os.path.expanduser('~/.bash_aliases')
    click.echo('Exporting aliases to {}'.format(path))
    with open(path, 'w') as f:
        f.write(bash_aliases)
