#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
from sys import platform

import requests
from huepy import *

filename = os.path.expanduser('~/.aerovane')
config = configparser.ConfigParser()


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def check_config():
    if os.path.isfile(filename):
        pass
    else:
        clear()
        print('It looks like you have not yet configured', bold(blue('AEROVANE')) + '.')

        owm_key = input('Please enter your OWM API key: ')
        config['OWM_API_KEY'] = {'owm_key': owm_key}

        ipstack_key = input('Please enter your ipstack API key: ')
        config['IPSTACK_API_KEY'] = {'ipstack_key': ipstack_key}

        degrees_pref = input('Would you like to see your temperature in'
                             ' degrees Celsius (C) or Fahrenheit (F)? ').lower()
        if degrees_pref == 'c':
            config['DEGREES'] = {'degrees': 'celsius'}
        else:
            config['DEGREES'] = {'degrees': 'fahrenheit'}

        with open(filename, 'w') as configfile:
            config.write(configfile)


def parse_config(value):
    response = ''
    config.read(filename)
    if value == 'owm_key':
        response = config['OWM_API_KEY']['owm_key']
    elif value == 'ipstack_key':
        response = config['IPSTACK_API_KEY']['ipstack_key']
    elif value == 'degrees':
        response = config['DEGREES']['degrees']

    return response


def get_location():
    api_key = parse_config('ipstack_key')

    ipstack_url = 'http://api.ipstack.com/check'
    query_params = {
        'access_key': api_key,
        'format': 1
    }

    response = requests.put(ipstack_url, params=query_params)
    location = response.json()['city'] + "," + response.json()['country_code']

    return location


def weather_report(owm, location, degrees):
    feels, temp = '', ''
    degree_marker = ('°' if platform == 'darwin' else '') + ('C' if degrees == 'celsius' else 'F')

    observation = owm.weather_at_place(location)
    weather = observation.get_weather()

    temperature = weather.get_temperature(degrees)
    humid = weather.get_humidity()
    wind = weather.get_wind()
    status = weather.get_detailed_status()

    if temperature['temp'] > (26.67 if degrees == 'celsius' else 80.0):
        feels, temp = bold(red('HOT!')), red(str(temperature['temp']) + degree_marker)
    elif temperature['temp'] > (20.0 if degrees == 'celsius' else 68.0):
        feels, temp = bold(yellow('WARM.')), yellow(str(temperature['temp']) + degree_marker)
    elif temperature['temp'] > (14.44 if degrees == 'celsius' else 58.0):
        feels, temp = bold(green('COOL.')), green(str(temperature['temp']) + degree_marker)
    elif temperature['temp'] > (8.89 if degrees == 'celsius' else 48.0):
        feels, temp = bold(lightblue('CHILLY.')), lightblue(str(temperature['temp']) + degree_marker)
    elif temperature['temp'] < (8.89 if degrees == 'celsius' else 48.0):
        feels, temp = bold(blue('COLD!')), blue(str(temperature['temp']) + degree_marker)

    location_name = location.split(',')[0].upper()

    clear()
    header = '    YOUR ' + bold(blue('AEROVANE')) + ' WEATHER REPORT FOR ' + bold(blue(location_name)) + '    '
    span = '-' * (41 + len(location_name))

    print(span)
    print(header)
    print(span)
    print('Current weather conditions:', bold(white(status.upper())))
    print(f'It\'s ' + feels + ' The current temperature is ' + temp + '.')
    print('Relative humidity is ' + green(str(humid) + '%') + '.')
    print('The wind speed is ' + orange(str(wind['speed']) + ' m/s') + '.')
    print(span + '\n')

