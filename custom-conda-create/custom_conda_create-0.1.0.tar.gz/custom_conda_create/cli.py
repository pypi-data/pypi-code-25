# -*- coding: utf-8 -*-

"""
Console script for custom_conda_create.
"""

import sys
import click
from . import custom_conda_create

@click.command()
@click.argument('env_name')
# def main(args=None):
def main(env_name=None):
    """
    Console script for custom_conda_create.
    """
    if not env_name:
        click.echo("See 'ccc --help' for more information.")
        sys.exit(1)
    custom_conda_create.run_conda_create(env_name)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
