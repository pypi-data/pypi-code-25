import click
from termcolor import cprint
from pyfiglet import figlet_format

from .lsbranch import lsBranch


@click.command(help='List all directories with .git subdirectory and show current branch for each')
@click.option('-r', '--recursive', default=False, is_flag=True, help='Recursive directory search')
@click.option('-p', '--path', type=click.Path(dir_okay=True), help='Path to search')
def cli(recursive, path):

    if not path:
        path = '.'

    click.clear()

    cprint(figlet_format('lsBranch', width=120), 'red')
    click.secho(' '*25 + 'by Ivan Arar', fg='red')

    lsbranch = lsBranch(path=path)

    click.echo()
    click.echo('-'*lsbranch.terminal_size)
    click.echo()

    lsbranch.search(recursive=recursive)

    click.echo('-'*lsbranch.terminal_size)
    click.echo()

    click.secho('Went through ' + str(lsbranch.counter_all()) + ' directories and found ' +
                str(lsbranch.counter_git()) + ' git repositories!', fg='blue', bold=True, blink=True)

    click.echo()
    click.echo('-'*lsbranch.terminal_size)
    click.echo()
