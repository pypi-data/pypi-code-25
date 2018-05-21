import os
import json
import logging.config
from argparse import ArgumentParser
from importlib.machinery import SourceFileLoader

import cherrypy
import yoyo
from cherrypy import daemon
from clor import configure

from .storage import createStorage


__all__ = 'bootstrap',


def bootstrap(config):
  '''Bootstrap application server'''

  logging.config.dictConfig(config['logging'])

  # If "global" is present it'll be used alone
  cherrypy.config.update(config.pop('global'))
  cherrypy.config.update(config)

  storageObj = createStorage(config['storage']['dsn'])

  cherrypy.tools.jsonify = jsonifyTool
  from . import controller

  api = cherrypy.tree.mount(controller.RecordApi(), '/api/v1/record', config['app']['api'])
  static = cherrypy.tree.mount(None, '/', config = config['app']['static'])
  for app in (api, static):
    app.storage = storageObj
    app.envconf = config


# CherryPy functions


def jsonifyTool(fn):
  '''Wrapper around built-in tool to pass ``default = str`` to encoder.'''

  def json_encode(value):
    for chunk in json.JSONEncoder(default = str).iterencode(value):
      yield chunk.encode()

  def json_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)  # @UndefinedVariable
    return json_encode(value)

  return cherrypy.tools.json_out(handler = json_handler)(fn) #@UndefinedVariable


def authenticate(realm, username, password):
  '''Basic Auth handler'''

  credentials = cherrypy.request.app.envconf['auth']
  return username == credentials['username'] and password == credentials['password']


# Command line functions


def serve(config, user = None, group = None, **kwargs):
  if user or group:
    cherrypy.process.plugins.DropPrivileges(
      cherrypy.engine, uid = user, gid = group, umask = 0o022).subscribe()

  bootstrap(config)
  daemon.start(**kwargs)


def migrate(config, **kwargs):
  migrations = yoyo.read_migrations(os.path.join(os.path.dirname(__file__), 'migration'))
  dsn = config['storage']['dsn'].replace('mysql://', 'mysql+mysqldb://')
  backend = yoyo.get_backend(dsn, migration_table = 'schema_version')
  backend.apply_migrations(backend.to_apply(migrations))


def main():
  p = ArgumentParser()
  sp = p.add_subparsers(dest='subparser')

  p.add_argument('-c', dest = 'envconf',
    default = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'envconf.py'),
    help = 'Override default envconf.py')
  p.add_argument('-e', dest = 'environment', default = 'development',
    help = 'Apply the given config environment')

  srv = sp.add_parser('serve')
  srv.add_argument('-d', action = 'store_true', dest = 'daemonize',
    help = 'Run the server as a daemon')
  srv.add_argument('-p', dest = 'pidfile', default = None,
    help = 'Store the process id in the given file')
  srv.add_argument('-u', dest = 'user', default = None,
    help = 'Run application as specified user')
  srv.add_argument('-g', dest = 'group', default = None,
    help = 'Run application as specified group')

  sp.add_parser('migrate')

  kwargs = vars(p.parse_args())

  cherrypy.config.environments.setdefault('development', {})
  cherrypy.config['environment'] = kwargs['environment']

  envconfs = SourceFileLoader('envconf', kwargs.pop('envconf')).load_module()
  config = configure(*getattr(envconfs, kwargs['environment']))

  cmd = kwargs.pop('subparser')
  if not cmd:
    p.print_help()
  else:
    globals()[cmd](config, **kwargs)

