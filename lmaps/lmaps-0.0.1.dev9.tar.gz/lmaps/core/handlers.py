#!/usr/bin/env python
import os
import sys
from .tasks import *
from .utils import *
from pluginbase import PluginBase
from jsonschema.exceptions import ValidationError

## Init plugins
plugin_dirs = [
  os.path.dirname(os.path.realpath(__file__)),
  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plugins'),
  os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../plugins'))
]
plugin_base = PluginBase(package='lmaps.plugins')
plugin_source = plugin_base.make_plugin_source(searchpath=plugin_dirs)


class Handler(object):
  '''
  Base class for handling /anything/
  '''

  context = None

  def __init__(self, **kwargs):
    '''
    Constructor
    '''
    self.context = kwargs['context']
    self.runner = kwargs['runner']
    self.kwargs = kwargs
    self.setup()

  def setup(self):
    '''
    Handles setting up this instance
    '''


class ManagerHandler(Handler):
  '''
  The handler used by the manager to get requests from clients and farm out work for workers
  '''

  def client_request(self, request):
    '''
    Handle an incoming request from a client
    :param request: The request from the client
    :return: A response to the client
    '''
    if not type(request) == type({}):
      return self.runner(error_message, client_message('Request must me a dictionary.', level=1))
    if request['list_units']:
      return self.runner(get_worker_units)
    if request['show_summary']:
      return self.runner(get_worker_units_instances,request['unit_name'])
    if request['create'] or request['apply']:
      return self.create_or_apply(request)
    if request['rollback']:
      return self.runner(rollback_worker_units_instances, request['unit_name'])
    return self.runner(error_message, client_message('Unable to fulfill request, {} does not seem valid.'.format(str(request)), level=1))

  def create_or_apply(self, request):
    '''
    Handle a request from the client to create or apply instances
    :param request: The request from the client
    :return: A response to the client
    '''
    instance = self.runner(validate_instance, request['unit_name'], request['instance'])
    unit = get_unit_by_name(request['unit_name'])
    unit_handler_name = unit['handler']['type']
    if type(instance) == ValidationError:
      return client_message(str(instance), level=1)
    try:
      unit_handler = plugin_source.load_plugin(unit_handler_name)
      try:
        args_schema = unit_handler.args_schema
        args = unit['handler']['args']
        validate(args, args_schema)
      except Exception as e:
        return client_message(
          'Cannot validate the schema of the handler "{}" args, this usually means that the config on the host is incorrect\n\n\tValidation error:\n\n{}'.format(
            unit_handler_name, str(e)), level=1)
      try:
        if request['create']:
          return unit_handler.instance_create(context=self.context, runner=self.runner, instance=instance, unit=unit)
        if request['apply']:
          return unit_handler.instance_apply(context=self.context, runner=self.runner, instance=instance, unit=unit)
      except Exception as e:
        return client_message('Failed to call {}.instance while handling\n\n{}\n\n'.format(unit_handler_name, e),
                              extra=instance, level=1)
    except:
      return client_message('Cannot load unit handler type "{}"'.format(unit_handler_name), extra=instance, level=1)
    return client_message('Instance create has been accepted\n', extra=instance)


class UnitHandler(Handler):
  '''
  Base class for unit handlers
  '''