#!/usr/bin/env python
"""Search enrolled Alexa For Business devices by MAC address, serial number, or name.

Usage:
    afb_search list [--profile=<profile>] [--region=<region>] [--mac-only]
    afb_search search (mac | serial | name) <search> [--profile=<profile>] [--region=<region>]
    afb_search (-h | --help)
    afb_search --version
    
Options:
    -h --help               Show this screen.
    --version               Show version.
    --mac-only              Only return the MAC instead of all device info.
    --profile=<profile>     Specify AWS profile (as defined in ~/.aws/credentials) - default "default".
    --region=<region>       Specify AWS region - default "us-east-1".
"""
from __future__ import print_function
import sys
from docopt import docopt
import boto3


def print_device(dev):
    return ('"{}" ({})\tSerial={}\tMAC={}\tRoom={}\t'
            'Version={}\tStatus={}/{}').format(dev.get('DeviceName', '<No Name>'),
                                               dev['DeviceType'],
                                               dev['DeviceSerialNumber'],
                                               dev['MacAddress'],
                                               dev.get('RoomName', '<none>'),
                                               dev['SoftwareVersion'],
                                               dev['DeviceStatus'],
                                               dev['DeviceStatusInfo']['ConnectionStatus'])


def list_devices(afb, mac_only):
    devices = afb.search_devices()['Devices']
    if len(devices) == 0:
        print('No Devices Found.', file=sys.stderr)
    else:
        for dev in devices:
            if mac_only:
                print(dev['MacAddress'])
            else:
                print(print_device(dev))


def search_mac(afb, mac):
    devices = afb.search_devices()['Devices']
    for dev in devices:
        if dev['MacAddress'] == mac.upper():
            print(print_device(dev))
            return
    print('No Devices Found.', file=sys.stderr)


def search_name(afb, name):
    devices = afb.search_devices(Filters=[
        {
            'Key': 'DeviceName',
            'Values': [name]
        }
    ])['Devices']
    if len(devices) == 0:
        print('No Devices Found.', file=sys.stderr)
    else:
        for dev in devices:
            print(print_device(dev))


def search_serial(afb, serial):
    devices = afb.search_devices(Filters=[
        {
            'Key': 'DeviceSerialNumber',
            'Values': [serial]
        }
    ])['Devices']
    if len(devices) == 0:
        print('No Devices Found.', file=sys.stderr)
    else:
        for dev in devices:
            print(print_device(dev))


def _main():
    arguments = docopt(__doc__, version='afb_search 1.0.2')

    aws_kwargs = {
        'region_name': 'us-east-1'
    }

    if arguments['--profile'] is not None:
        aws_kwargs['profile_name'] = arguments['--profile']
    if arguments['--region'] is not None:
        aws_kwargs['region_name'] = arguments['--region']

    aws_session = boto3.Session(**aws_kwargs)
    afb = aws_session.client('alexaforbusiness')

    if arguments['list']:
        list_devices(afb, arguments['--mac-only'])
    elif arguments['search']:
        search = arguments['<search>']
        if arguments['mac']:
            search_mac(afb, search)
        elif arguments['serial']:
            search_serial(afb, search)
        elif arguments['name']:
            search_name(afb, search)


if __name__ == '__main__':
    _main()
