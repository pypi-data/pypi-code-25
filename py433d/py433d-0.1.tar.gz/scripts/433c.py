#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit

from py433 import (
    client,
    __version__,
    defaults
)

parser = ArgumentParser(description='Client for 433d server')
parser.add_argument('-o', '--host', default='localhost', help="Set host to connect to")
parser.add_argument('-v', '--version', action='store_true', help="Show version")
parser.add_argument('-p', '--port', default=defaults.port, help="Set port to connect to")
parser.add_argument('message', metavar='message', type=str, help='Code to send')
args = parser.parse_args()

if args.version:
    print(__version__)
    exit(0)

clt = client(host=args.host, port=args.port)
clt.send(args.message)
