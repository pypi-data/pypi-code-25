#!/usr/bin/env python3

import argparse
import os
import os.path
import sys
from hashlib import md5, sha224, sha512

parser = argparse.ArgumentParser(
    description="Rename photos to give them more generic and unified names")
"""parser.add_argument("-v", "--verbose",
                    help="increase output verbosity", action="store_true")"""
parser.add_argument(
    "-a", "--all", help="rename all files in the current directory", action="store_true")
parser.add_argument("-i", "--input_file",
                    help="set the input file to be renamed", type=str)
parser.add_argument("-o", "--output_path",
                    help="set the output files location", type=str)
parser.add_argument(
    "--md5", help="use md5 to rename output file", action="store_true")
parser.add_argument(
    "--sha224", help="use sha224 to rename output file", action="store_true")
parser.add_argument(
    "--sha512", help="use sha512 to rename output file", action="store_true")
args = parser.parse_args()


def verbose(args, string):
    if args.verbose:
        print(string)


def get_md5_string(input_file):
    m = md5()
    m.update(input_file)
    md5string = str(m.hexdigest())
    return md5string


def get_sha224_string(input_file):
    s = sha224()
    s.update(input_file)
    sha224string = str(s.hexdigest())
    return sha224string


def get_sha512_string(input_file):
    s = sha512()
    s.update(input_file)
    sha512string = str(s.hexdigest())
    return sha512string


def rename():
    try:
        verbose(args, "Input File: " + os.path.realpath(args.input_file))
        in_f = os.path.realpath(args.input_file)
    except TypeError:
        print("You must specify an input file.")
        sys.exit(1)
    _, f_ext = os.path.splitext(in_f)
    if args.output_path:
        output_path = "{0}//".format(os.path.realpath(args.output_path))
    else:
        output_path = "{0}//".format(os.getcwd())
    if args.md5:
        out_f = "{0}\\{1}{2}".format(output_path, get_md5_string(
            args.input_file.encode('utf-8')), f_ext)
    elif args.sha224:
        out_f = "{0}\\{1}{2}".format(output_path, get_sha224_string(
            args.input_file.encode('utf-8')), f_ext)
    elif args.sha512:
        out_f = "{0}\\{1}{2}".format(output_path, get_sha512_string(
            args.input_file.encode('utf-8')), f_ext)
    try:
        verbose(args, "Output File: " + out_f)
        os.rename(in_f, out_f)
    except IOError as error:
        print(error)
        sys.exit(1)
