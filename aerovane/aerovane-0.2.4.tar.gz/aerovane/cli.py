#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pyowm
import click
from .aerovane import check_config, parse_config, get_location, weather_report


@click.command()
@click.option('--location', '-l', callback=check_config(), default=get_location(),
              help='Overrides default location based on your IP. Takes a string of city name and two letter country '
                   'code (separated by a comma), for example: \'Los Angeles, US\'.')
@click.option('--degrees', '-d', callback=check_config(), default=parse_config('degrees'), type=click.Choice(['celsius', 'fahrenheit']),
              help='Overrides degrees preference stored in the config file. Takes either fahrenheit'
                   ' or celsius as values.')
def cli(location, degrees):
    """
    Aerovane is a simple CLI for generating a weather report in your terminal.
    """

    owm_key = parse_config('owm_key')
    owm = pyowm.OWM(owm_key)
    weather_report(owm, location, degrees)
    pass

