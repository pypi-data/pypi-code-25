from __future__ import absolute_import
from . import printer
from . import validator
import click
import json
import sys


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-a', '--all-errors', is_flag=True,
              help='Print all errors. [default: only the first error of each kind]')
@click.option('-v', '--value', is_flag=True,
              help='Print cell values in error report. [default: False]')
@click.argument('input', type=click.Path(exists=True))
@click.version_option()
def main(all_errors, value, input):
    """A tool to validate Opedia dataset files."""
    errors = validator.validate(input)
    printer.print_tsv_errors(errors, sys.stdout, print_all=all_errors,
                             header=True, print_value=value)
