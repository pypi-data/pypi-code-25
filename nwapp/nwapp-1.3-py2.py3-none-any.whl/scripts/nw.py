

import os
import sys
import argparse
#from contract_process import *
from pymongo import MongoClient
from pprint import pprint
import datetime
import click
import pandas as pd

conn = MongoClient('localhost', port=14041)

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
@click.argument('action_type',type=str,default='view', required=False)
@click.argument('title',type=str,default='No title', required=False)
@click.argument('amount',type=float,default=0.00, required=False)
def cud(action_type, title, amount):
    """This function operates on contracts under deliberation"""
    db = conn.workdb_test
    table = db.cud_db
    
    if action_type == "view":
        cud_data = []
        for document in table.find():
            cud_data.append(document)
        df = pd.DataFrame(cud_data)
        print('\n\n Contract Under Deliberation: View\n\n')
        print(' INFO')
        print('------')
        print(df[['title','amount']])
        print('\n SUMMARY')
        print('---------')
    else:
        response = table.insert([{"title": title,"amount":amount}])
        print(response)


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
@click.option('-s','--string', nargs=+1, default='World', help='This is the thing that is greeted.')
@click.argument('out', type=str, default='No title', required=False)
def caa(out, string):
    """This function operates on contracts for which payment has arrived"""
    print(out)
    print(string)


if __name__ == '__main__':
    
    cli()