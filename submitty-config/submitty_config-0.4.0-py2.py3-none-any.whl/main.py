#!/usr/bin/env python3

from argparse import ArgumentParser, PARSER, RawDescriptionHelpFormatter
import os

from . import __VERSION__

import json
import jsonschema


class SubcommandHelpFormatter(RawDescriptionHelpFormatter):
    def _format_action(self, action):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        parts = super()._format_action(action)
        if action.nargs == PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


def lint(file_path):
    with open(os.path.join(os.getcwd(), file_path)) as open_file:
        json_obj = json.load(open_file)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, 'schema.json')) as open_file:
        schema_obj = json.load(open_file)
    jsonschema.validate(json_obj, schema_obj)


def parse_args():
    parser = ArgumentParser(formatter_class=SubcommandHelpFormatter)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __VERSION__)
    subparser = parser.add_subparsers(metavar='command', dest='command')
    lint_parser = subparser.add_parser('lint', help='lint a config file')
    lint_parser.add_argument('file', help='path to config file to lint')
    return parser.parse_args()


def run():
    args = parse_args()
    if args.command == 'lint':
        lint(args.file)
        print("Lint Successful")
