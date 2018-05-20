#!/usr/bin/env python
'''
Tasks that can be run on workers.
'''

from .utils import *


def no_work(context):
  '''
  Do nothing.
  :param context: The runner's instance
  :return: dict
  '''
  return {}


def error_message(context, msg):
  '''
  Cannot remember, maybe I was starting to setup a logging facility?
  :param context: The runner's instance
  :param msg:
  :return:
  '''
  return msg


def stop_worker_thread(context):
  '''
  Inform a worker that it needs to die.
  :param context: The runner's instance
  :return:
  '''
  context.stop()
  return {}


def get_worker_config(context):
  '''
  Get the config from the worker's perspective.
  :param context: The runner's instance
  :return:
  '''
  try:
    return context.config
  except:
    return client_message('No configuration has been injected into this worker', level=1)


def get_worker_units(context):
  '''
  Get installed units from the worker's perspective.
  :param context: The runner's instance
  :return:
  '''
  try:
    return context.config['units']
  except:
    return client_message('No configuration has been injected into this worker', level=1)


def get_worker_units_instances(context, name):
  '''
  Get instances of a unit based on the unit's name.
  :param context: The runner's instance
  :param name: Name of unit
  :return:
  '''
  try:
    unit = get_unit_by_name(name)
    data = get_data_type_by_name(unit['meta']['data_type'])(
      store_root=unit['meta']['store_root'],
      store_key=unit['meta']['store_key']
    )
    return client_message('Instances:', extra=data.state())
  except:
    return client_message('Cannot', level=1)


def rollback_worker_units_instances(context, name):
  '''
  Perform a rollback on the workers local datastore.
  :param context: The runner's instance
  :param name: Name of unit
  :return:
  '''
  unit = get_unit_by_name(name)
  data = get_data_type_by_name(unit['meta']['data_type'])(
    store_root=unit['meta']['store_root'],
    store_key=unit['meta']['store_key']
  )
  before = data.state()
  removing = data.rollback()
  after = data.state()
  if removing == []:
    return client_message('Nothing to rollback, the instance is empty')
  else:
    return client_message('', extra=[{"removing": removing}, {"before": before}, {"after": after}])


def validate_instance(context, unit_name, instance):
  '''
  Determine if a dict is a valid instance request based on the schema of the unit
  as well as apply defaults from the schema.
  :param context: The runner's instance
  :param unit_name: String name of unit
  :param instance: Dict the instance to validate
  :return: Dict the valid and default-mixed-in instance
  '''
  unit = get_unit_by_name(unit_name, config=context.config)
  instance = validate_unit_instance(instance, unit)
  return instance

