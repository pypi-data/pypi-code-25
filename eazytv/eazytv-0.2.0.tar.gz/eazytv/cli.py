
import click
from tabulate import tabulate

from .utils import read_version
from .eztv.database import ShowDB

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def which_filter(status):

    _filters = {
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
pass_db = click.make_pass_decorator(ShowDB, ensure=True)


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(version=read_version())
def cli():
    pass


@cli.command(
    name='showlist',
    help="Display your favorites"
)
@click.option(
    '--status', type=click.Choice(['airing', 'ended', 'on-break', 'pending'])
)
@click.option(
    '--count', is_flag=True
)
@pass_db
def shows(db, status, count):

    if count:
        click.echo("There are actually {} shows on EZTV".format(db.length))
        exit(0)

    header = ['Name', 'Status', 'Rating']
    if status is not None:
        _filter = which_filter(status)
        table = [
            (show[0], show[2], show[3])
            for show in db.shows
            if _filter in show[2]
        ]
    else:
        table = [
            (show[0], show[2], show[3])
            for show in db.shows
        ]

    print(tabulate(table, header, tablefmt="grid"))
