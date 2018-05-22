#!/usr/bin/env python
import os
import sys
import json
import yaml
import argparse
from lmaps.core import config
from lmaps.core.utils import verbose, debug, fatal, client_message
from lmaps.core.client import Client

manager_schema_config_path     = os.path.expanduser('~/.config/lmaps')
manager_schema_config_filepath = os.path.join(manager_schema_config_path,'manager_schema.yaml')


def get_default_parser():
  '''
  Get shell default args for command line usage
  :return: argparse namespace
  '''
  parser = argparse.ArgumentParser(description='Lightweight Management and Provisioning Service')
  parser.add_argument('--version', action='version', version='%(prog)s 1.0')
  parser.add_argument('--file', '-f', dest="instance", help='Yaml file with which to perform operations')
  parser.add_argument('--config', dest="config_file", help='Config file')
  parser.add_argument('--format', dest="format", help='Output format', default='yaml')
  parser.add_argument('--daemon', '-D', dest="daemon", action='store_true', help='Run as a daemon', default=False)
  parser.add_argument('--discover', dest="discover_endpoint", action='store', default=False, help='URI of endpoint to discover (run if the help info is empty)')
  debug(parser)
  return parser


def get_parser(schema=None):
  '''
  Get shell args for command line usage,
  either the default or if an endpoint has been discovered,
  the manager's schema as well
  :return: argparse namespace
  '''
  if not schema:
    p = get_default_parser()
    debug(p)
    return p
  else:
    parser = get_default_parser()
    switches_used = ['-f', '-D']
    for dest in schema['properties']:
      switches = ['--{}'.format(dest.replace('_','-'))]
      alts = ['-{}'.format(dest[0]),'-{}'.format(dest[0].upper())]
      for alt in alts:
        if not alt in switches_used:
          switches.append(alt)
          switches_used.append(alt)
          break
      canidate_args = {}
      canidate_args['action'] = 'store'
      if schema['properties'][dest]['type'] == 'boolean':
        canidate_args['action'] = 'store_true'
      if 'default' in schema['properties'][dest]:
        canidate_args['default'] = schema['properties'][dest]['default']
      if 'title' in schema['properties'][dest]:
        canidate_args['help'] = schema['properties'][dest]['title']
      parser.add_argument(*switches, **canidate_args)
    debug(parser)
    return parser


def print_response(msg, format='dict'):
  '''
  Prints dictionaries in a human readable way
  :param msg: message to make human readable
  :param format: How to format the msg (i.e. coercion strategy)
  '''
  debug(msg)
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


def discover_endpoint(args):
  '''
  Reach out to an endpoint and request its manager's schema
  :param args: Argparse namespace
  :return: Boolean the status of the recovery
  '''
  if not os.path.isdir(manager_schema_config_path):
    os.makedirs(manager_schema_config_path)
  cfg = {
    "rpc": {
      "manager_bind": args.discover_endpoint
    }
  }
  try:
    debug('Trying to merge discovery bind uri into loaded config')
    cfg = dict(config.load_config(config_file=args.config_file).items() + cfg.items())
  except:
    debug('Failed to merge discovery bind uri into loaded config')
    pass
  c = Client(cfg['rpc']['manager_bind'])
  response = c.request({"discover": "schema"})
  debug(response, 'This is the response from the manager')
  try:
    assert not response == None
  except:
    fatal_message = """Got 'None' as a response when trying to discover against the manager,
    this is probably because the manager sent to response and a timeout occured.
    Is the manager running on the URI?"""
    debug('Was unable to rx a response', fatal_message)
    fatal(fatal_message)
  if 'level' in response:
    if not response['level'] == 0:
      debug(response, 'The message in the response is telling me to fail')
      fatal(response['message'])
  else:
    raise Exception('No level was in the response')
  manager_schema_config_safe_filename = cfg['rpc']['manager_bind'].replace(':', '-').replace('/', '_')
  for path in [manager_schema_config_filepath,
               os.path.join(manager_schema_config_path, manager_schema_config_safe_filename)]:
    with open(path, 'w') as f:
      debug('Writing manager schema to {}'.format(path))
      file_content = yaml.safe_dump(response['extra'])
      #print(json.dumps(client_message("Discovered endpoint as:", extra=file_content), indent=2))
      f.write(file_content)
  return True


def arg_rules(args):
  '''
  Takes in the current args and verifies and salts them
  :param args: Argparse namespace
  :return: Argparse namespace
  '''
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
  debug(args)
  return args


def start():
  '''
  Start the CLI
  '''
  schema = None
  if os.path.isfile(manager_schema_config_filepath):
    with open(manager_schema_config_filepath, 'r') as f:
      schema = yaml.load(f.read())
  parser = get_parser(schema)
  args = parser.parse_args()
  if args.config_file:
    cfg = config.load_config(config_file=args.config_file)
  else:
    try:
      cfg = config.load_config()
    except:
      parser.print_help()
      fatal()
  if args.discover_endpoint:
    if discover_endpoint(args):
      sys.exit(0)
    else:
      fatal()
  if args.daemon:
    from lmaps.core.daemon import Daemon
    d = Daemon(config=cfg)
    d.run()
  else:
    args = arg_rules(args)
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
