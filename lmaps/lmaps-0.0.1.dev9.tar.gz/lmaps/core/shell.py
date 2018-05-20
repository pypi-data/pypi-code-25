#!/usr/bin/env python
import sys
import json
import yaml
import argparse
from lmaps.core import config
from lmaps.core.client import Client


def get_parser():
  '''
  Get shell args for command line usage
  :return: argparse namespace
  '''
  parser = argparse.ArgumentParser(description='Lightweight Management and Provisioning Service')
  parser.add_argument('--version', action='version', version='%(prog)s 1.0')
  parser.add_argument('--config', dest="config_file", help='Config file')
  parser.add_argument('--format', dest="format", help='Output format', default='yaml')
  parser.add_argument('--create', '-c', action="store_true", default=False, dest="create", help='Create an instance')
  parser.add_argument('--apply', '-a', action="store_true", default=False, dest="apply", help='Apply the instance(s)')
  parser.add_argument('--rollback', action="store_true", default=False, dest="rollback", help='Remove the newest instance from the unit')
  parser.add_argument('--unit', '-u', dest="unit_name", help='Name of unit on which actions are performed')
  parser.add_argument('--file', '-f', dest="instance", help='Yaml file with which to perform operations')
  parser.add_argument('--daemon', '-D', dest="daemon", action='store_true', help='Run as a daemon', default=False)
  parser.add_argument('--list-units', '-l', dest="list_units", action='store_true', default=False, help='List units')
  parser.add_argument('--show-summary', '-S', dest="show_summary", action='store_true', default=False, help='List instances')
  return parser


def print_response(msg, format='dict'):
  '''
  Prints dictionaries in a human readable way
  :param msg: message to make human readable
  :param format: How to format the msg (i.e. coercion strategy)
  '''
  if not msg == {}:
    if not msg:
      print('Empty response "{}"'.format(str(msg)))
    else:
      if format == 'dict':
        print(msg)
      elif format == 'json':
        print(json.dumps(msg))
      elif format == 'pretty':
        print(json.dumps(msg, indent=2))
      elif format == 'yaml':
        print(yaml.safe_dump(msg, width=50, indent=2, default_flow_style=False))


def start():
  '''
  Start the CLI
  :param args: Argparse namespace
  '''
  parser = get_parser()
  args = parser.parse_args()
  if args.config_file:
    cfg = config.load_config(config_file=args.config_file)
  else:
    try:
      cfg = config.load_config()
    except:
      parser.print_help()
      sys.exit(1)
  if args.daemon:
    from lmaps.core.daemon import Daemon
    d = Daemon(config=cfg)
    d.run()
  else:
    if args.rollback and not args.unit_name:
      raise Exception("'--rollback' requires '--unit' (units can be listed with '--list-units')")
    if args.show_summary and not args.unit_name:
      raise Exception("'--list-instances' requires '--unit' (units can be listed with '--list-units')")
    if (args.create or args.apply) and not args.unit_name or \
        args.create and not (args.instance and args.unit_name):
      raise Exception("'--create' requires both '--file' and '--unit' and '--apply' requires '--unit'")
    if args.instance:
      with open(args.instance, 'r') as f:
        args.instance = yaml.load(f.read())
    c = Client(cfg['rpc']['manager_bind'])
    response = c.request(vars(args))
    if 'message' in response:
      print(response['message'])
      if 'message' in response:
        print('')
        print_response(response['extra'], args.format)
      if 'level' in response:
        sys.exit(response['level'])
    else:
      print_response(response, args.format)
