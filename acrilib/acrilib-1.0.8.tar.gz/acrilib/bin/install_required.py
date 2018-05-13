#!/usr/bin/env python3
'''
Created on Jan 2, 2018

@author: arnon
'''

from subprocess import run, PIPE
from acrilib.setup.install_required import install_required, format_file_required, format_setup_required


def cmdargs():
    import argparse

    parser = argparse.ArgumentParser(
        description='''produce required packages to add into setup.py.

Example:
    install_required
    ''')

    parser.add_argument('--exact', action='store_true', dest='exact', default=False,
                        help='set relationships as ==, otherwise >= will be used.')
    parser.add_argument('--embed', action='store_true', dest='embed', default=False,
                        help='format for embedding directly into setup.py.')
    parser.add_argument('--output', type=str, dest='output', required=False, default='REQUIRED',
                        help='override the default "REQUIRED" file.')
    args = parser.parse_args()
    return args


def main(args):
    required = install_required(args.exact)
    if not args.embed:
        msg = format_file_required(required, file=args.output)
    else:
        msg = format_setup_required(required)
        print(msg)


if __name__ == '__main__':
    args = cmdargs()
    main(args)

    