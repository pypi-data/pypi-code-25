#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import imp

import svdog


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='config file', action='store', required=False)
    parser.add_argument('-v', '--version', action='version', version='%s' % svdog.__version__)
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


def run():
    args = build_parser().parse_args()

    app = svdog.SVDog(config=load_config(args.config) if args.config else None)
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
 
if __name__ == '__main__':
    run()
