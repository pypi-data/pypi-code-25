import click
import sys
import os

from .. import CONFIG


@click.command()
def config():
    #turn stdout into something you can write bytes to
    CONFIG.write(os.fdopen(sys.stdout.fileno(), 'wb'))
