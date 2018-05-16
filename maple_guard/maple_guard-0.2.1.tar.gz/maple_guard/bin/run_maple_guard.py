#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

import imp
import argparse
import sys

import maple_guard
from maple_guard import Server, constants


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--host', default=constants.HOST, help='bind host', action='store')
    parser.add_argument('-p', '--port', type=int, default=constants.PORT, help='bind port', action='store')
    parser.add_argument('-c', '--config', help='config file', action='store', required=True)
    parser.add_argument('-v', '--version', action='version', version='%s' % maple_guard.__version__)
    return parser


def load_config(filename):
    d = imp.new_module('config')
    d.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return d


def run_maple_guard():
    args = build_parser().parse_args()

    app = Server(config=load_config(args.config))

    try:
        app.run(args.host, args.port)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    run_maple_guard()
