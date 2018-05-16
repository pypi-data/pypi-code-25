import os
import re
import shutil
import urllib.request

import click
import git
import bs4
import yaml
from click import ClickException

from oversee import terminal, jetbrains, extensions, gitignore
from oversee import config
from oversee.gitignore import GitIgnore


@click.group()
def main():
    pass


@click.command()
@extensions.list_options(config.install)
@click.argument('name')
def install(name):
    """Installs a module defined in the .yaml file. Options include: {}"""
    terminal.install(name)


@click.command()
@extensions.list_options(config.aliases)
@click.argument('name')
def export(name):
    """Exports your bash aliases to .bash_aliases!"""
    terminal.export_aliases(name)


@click.command()
@extensions.list_options(jetbrains.options)
@click.argument('name')
def sync(name):
    """Sync you a specific IDE with your saved settings!"""
    jetbrains_root = jetbrains.get_path(name)
    click.echo('Syncing settings to {}'.format(jetbrains_root))

    path = os.path.join(jetbrains_root, 'config')
    for file in config.jetbrains:
        dst = os.path.join(path, file)
        src = os.path.join(os.path.expanduser('~'), '.oversee', 'jetbrains', file)
        if not os.path.exists(src):
            click.echo('{} does not exist and is not being synced.')
        else:
            click.echo('Copying {} to {}'.format(file, dst))

        shutil.copy(src, dst)


@click.command()
@extensions.list_options(jetbrains.options)
@click.argument('name')
def save(name):
    """Save your the settings of a jetbrains IDE to a common location so they can be synced with the other IDEs."""
    path = jetbrains.get_path(name)
    click.echo('Saving settings from {}'.format(path))

    directory = os.path.join(path, 'config')
    for file in config.jetbrains:
        src = os.path.join(directory, file)
        dst = os.path.join(os.path.expanduser('~'), '.oversee', 'jetbrains', file)
        if not os.path.exists(src):
            click.echo('{} does not exist and is not being saved.')
        else:
            click.echo('Copying {} to {}'.format(file, dst))

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)


@click.command()
@extensions.list_options(config.environments)
@click.argument('name')
def setup(name):
    """Setup an environment!"""
    if name not in config.environments:
        click.echo('{} does not exist :('.format(name))
        return
    else:
        click.echo('Setting up {}!'.format(name))

    environment = config.environments[name]
    for item in environment.get('install', []):
        terminal.install(item)

    for repository in environment.get('clone', []):
        url = repository['repository']
        dst = repository['to']
        dst = os.path.expanduser(dst)

        if os.path.exists(dst):
            click.echo('Skipping {}. Folder exists!'.format(dst))
            continue

        name, _ = os.path.basename(url).split('.')
        click.echo('Cloning {} to {}'.format(name, dst))

        to_path = os.path.join(dst, name)
        os.makedirs(dst, exist_ok=True)
        git.Repo.clone_from(url, to_path=to_path)


@click.group()
def project():
    pass


@click.command()
def exportignore():
    """Exports your .gitignore.yaml to a .gitignore file!"""
    local = GitIgnore.from_local()

    inherit = gitignore.project_gitignore.get('inherit', [])
    for name in inherit:
        local.extend(GitIgnore(name))

    path = os.getcwd()
    local.export(path)


@click.command()
@click.argument('version')
def release(version):
    path = os.path.join(os.getcwd(), 'setup.py')
    if not os.path.exists(path):
        click.echo('setup.py does not exist :(')
        return

    with open(path) as f:
        contents = f.read()

    pattern = '(version=\')([0-9.]+)(\')'
    try:
        old_version = re.search(pattern, contents).group(2)
    except AttributeError:
        click.echo('No version could be parsed out of {}'.format(path))
        return

    click.echo('Incrementing setup.py from {} to {}'.format(old_version, version))

    contents = re.sub(pattern, '\g<1>{}\g<3>'.format(version), contents)
    with open(path, 'w') as f:
        f.write(contents)

    if click.confirm('Make version commit?'):
        message = click.prompt('Enter commit message: ', default=version)
        terminal.run('git add .')
        terminal.run('git commit -m "{}"'.format(message))

    if click.confirm('Make release tag?'):
        terminal.run('git tag {}'.format(version))

    if click.confirm('Upload to PyPi?'):
        terminal.run('python setup.py sdist')
        terminal.run('python setup.py sdist upload')


project.add_command(exportignore)
project.add_command(release)

main.add_command(install)
main.add_command(export)
main.add_command(save)
main.add_command(sync)
main.add_command(setup)
main.add_command(project)


if __name__ == '__main__':
    main()
