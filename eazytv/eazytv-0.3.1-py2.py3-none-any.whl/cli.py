
import click
from tabulate import tabulate

from .utils import read_version, fuzzy_matches
from .eztv.eztv import EZTVManager

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def which_filter(status):

    _filters = {
        None: None,
        'airing': 'Airing',
        'ended': 'Ended',
        'on-break': 'On break',
        'pending': 'Pending'
    }

    return _filters[status]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
pass_manager = click.make_pass_decorator(EZTVManager, ensure=True)


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(version=read_version())
def cli():
    pass


@cli.command(
    name='showlist',
    help="Display the showlist"
)
@click.option(
    '--status', type=click.Choice(['airing', 'ended', 'on-break', 'pending'])
)
@click.option(
    '--count', is_flag=True
)
@pass_manager
def shows(manager, status, count):

    if count:
        click.echo("There are actually {} shows on EZTV".format(manager.count))
        exit(0)

    header = ['Id', 'Name', 'Status', 'Rating']
    status = which_filter(status)

    table = [
        (show[0], show[1], show[3], show[4])
        for show in manager.filter_by_status(status)
    ]

    print(tabulate(table, header, tablefmt="grid"))


@cli.command(
    name='search',
    help="Search a show"
)
@click.argument(
    'show', required=True
)
@pass_manager
def search(manager, show):

    matches = fuzzy_matches(manager.names, show)
    if not matches:
        click.echo("{} does not exists in EZTV".format(show))
        exit(1)

    table = [
        manager.find_show(match)
        for match in matches
    ]

    header = ['Id', 'Name', 'Status', 'Rating']
    print(tabulate(table, header, tablefmt="grid"))
