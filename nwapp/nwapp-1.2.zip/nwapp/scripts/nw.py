

import os
import sys
import argparse
#from contract_process import *
from pymongo import MongoClient
from pprint import pprint
import datetime
import click

class Config(object):

    def __init__(self):
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    if verbose:
        click.echo('We are in verbose mode.')

@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
@click.pass_context
def cud(string, repeat, out):
    """This function operates on contracts under deliberation"""
    
    if verbose:
        click.echo('We are in say verbose mode')
    for x in range(repeat):
        click.echo('Hello {}!'.format(string), file=out)
    print("I am editing contracts under discussion")


@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def co(string, repeat, out):
    """This function operates on ongoing contracts"""
    pass


@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def cpt(string, repeat, out):
    """This function operates on contracts pending transfer of due amount"""
    pass

@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def cat(string, repeat, out):
    """This function operates on contract payment is in transit"""
    pass

@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def caa(string, repeat, out):
    """This function operates on contracts for which payment has arrived"""
    pass


if __name__ == '__main__':
    cli()