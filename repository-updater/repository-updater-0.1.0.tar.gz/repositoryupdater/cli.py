"""
CLI Module

Handles CLI for the Repository Updater
"""
from os import environ
from sys import argv

import click
import crayons

from .github import GitHub
from .repository import Repository


@click.command()
@click.option('--token', hide_input=True, prompt="GitHub access token",
              help="GitHub access token")
@click.option('--repository', prompt="Hassio Addons repository to update",
              help="The Hassio Addons repository to update, e.g., "
                   "hassio-addons/repository")
@click.option('--addon', help='Update a single/specific add-on')
@click.option('--force', is_flag=True,
              help='Force an update of the add-on repository')
def repository_updater(token, repository, addon, force):
    """Generic CLI Bootstrap"""
    click.echo(crayons.blue('Community Hass.io Add-ons Repository Updater',
                            bold=True))
    click.echo(crayons.blue('-' * 50, bold=True))
    github = GitHub(token)
    click.echo("Authenticated with GitHub as %s" %
               crayons.yellow(github.get_user().name, bold=True))
    repository = Repository(github, repository, addon, force)
    repository.update()
    repository.cleanup()


def git_askpass():
    """
    Short & sweet script for use with git clone and fetch credentials.
    Requires GIT_USERNAME and GIT_PASSWORD environment variables,
    intended to be called by Git via GIT_ASKPASS.
    """
    if argv[1] == "Username for 'https://github.com': ":
        print(environ['GIT_USERNAME'])
        exit()

    if argv[1] == "Password for 'https://" \
            "%(GIT_USERNAME)s@github.com': " % environ:
        print(environ['GIT_PASSWORD'])
        exit()

    exit(1)
