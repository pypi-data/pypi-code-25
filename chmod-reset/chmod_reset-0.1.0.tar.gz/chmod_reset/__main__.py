# -*- coding: utf-8 -*-
import os
import argparse

from .chmod_reset import scan

def main(argv=None):
    '''Main entry point'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action='store_true', help='Disable verbose output')
    parser.add_argument('path', help='Working file/directory to `chmod`')

    args, _ = parser.parse_known_args(argv)    
    scan(args.path, not(args.quiet))
