import os
import re
import shutil
import urllib.request

import click
import git
import bs4

from oversee import terminal, jetbrains, extensions
from oversee import config


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
@extensions.list_options(config.gitignores)
@click.argument('name')
@click.option('--path')
def initignore(name, path):
    path = path or '.'

    name = name.lower()
    name = '{}.gitignore'.format(name)
    urls = ['https://github.com/github/gitignore', 'https://github.com/github/gitignore/tree/master/Global']
    for url in urls:
        resp = urllib.request.urlopen(url)
        soup = bs4.BeautifulSoup(resp, "html.parser", from_encoding=resp.info().get_param('charset'))

        for link in soup.find_all('a', href=True):
            title = link.get('title', '')
            title = title.lower()
            if title != name:
                continue

            source = link.get('href')
            source = 'https://raw.githubusercontent.com{}'.format(source)
            source = source.replace('/blob', '')
            click.echo('Grabbing .gitignore from {}'.format(source))

            official_gitignore = urllib.request.urlopen(source).read().decode().split('\n')
            official_gitignore = [line.strip() for line in official_gitignore]

            folder = os.path.join(os.getcwd(), path)
            folder = os.path.normpath(folder)
            file = os.path.join(folder, '.gitignore')
            if not os.path.exists(file):
                if not click.confirm('Create .gitignore in {}?'.format(folder)):
                    return
                gitignore = []
            else:
                click.echo('Modifying {}'.format(file))

                with open(file, 'r') as f:
                    gitignore = f.readlines()
                    gitignore = [line.strip() for line in gitignore]

            to_append = []
            for line in official_gitignore:
                if not line or line.startswith('#') or line in gitignore:
                    continue

                to_append.append(line)

            if not to_append:
                click.echo('.gitignore is already up to date :)')
                return
            else:
                click.echo('Appending {} lines'.format(len(to_append)))

            if gitignore:
                gitignore.append('\n')

            gitignore.append('### Generated by oversee ###')
            gitignore.extend(to_append)
            gitignore.append('###########################')

            with open(file, 'w') as f:
                f.write('\n'.join(gitignore))

            return
    else:
        click.echo('No .gitignore files found :(')


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
    old_version = re.search(pattern, contents).group(2)
    click.echo('Incrementing setup.py from {} to {}'.format(old_version, version))

    contents = re.sub(pattern, '\g<1>{}\g<3>'.format(version), contents)
    with open(path, 'w') as f:
        f.write(contents)

    if click.confirm('Upload to PyPi?'):
        terminal.run('python setup.py sdist')
        terminal.run('python setup.py sdist upload')

    if click.confirm('Make release tag?'):
        terminal.run('git tag {}'.format(version))


project.add_command(initignore)
project.add_command(release)

main.add_command(install)
main.add_command(export)
main.add_command(save)
main.add_command(sync)
main.add_command(setup)
main.add_command(project)


if __name__ == '__main__':
    main()
