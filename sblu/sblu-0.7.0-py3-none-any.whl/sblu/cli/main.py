import click

from . import make_cli_class, setup_for_command_line
from ..version import version

from .util import config


def make_subcommand(package):
    @click.command(package, cls=make_cli_class(package))
    def cli():
        pass
    return cli


@click.group('sblu')
@click.option('-v', '--verbose', count=True)
@click.version_option(version=version)
def cli(verbose):
    setup_for_command_line(verbose)


for subcommand in ('pdb', 'docking', 'measure', 'cluspro', 'ftmap'):
    sub_cli = make_subcommand(subcommand)
    cli.add_command(sub_cli)

cli.add_command(config)
