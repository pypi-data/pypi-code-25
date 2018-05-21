#!/usr/bin/env python
'''
Handy functions and objects
'''

import sys
from .config import load_config, validate, applySchemaDefaults, ValidationError
from lmaps.core.data import *


def client_message(message, level=0, extra={}):
  '''
  Create a properly formatted dict that can be handled
  by the client shell when the manager replies.
  :param message: String the main message
  :param level: Int more or the exit code you wish the client to experience
  :param extra: Dict extra debug info if needed
  :return: Dict the message to reply to the client with
  '''
  return {"message":str(message), "level": level, "extra":extra}


def get_unit_by_name(name, config=None):
  '''
  For a given config, return a unit by its name.
  :param name: String name of the unit
  :param config: Dict the config to compare
  :return: Dict the unit found
  '''
  if not config:
    config = load_config()
  canidate_unit = {}
  for unit in config['units']:
    if unit['meta']['name'] == name:
      canidate_unit = unit
  assert not canidate_unit == {}
  return canidate_unit


def validate_unit_instance(instance, unit):
  '''
  Locally validate and mixin schema defaults
  for a given instance by the unit to be applied.
  :param instance: Dict the instance to try
  :param unit: Dict the unit containing the schema
  :return: Dict the valid, mixed instance or an error containing what and why the instance is not valid
  '''
  try:
    validate(instance, unit['params'])
  except ValidationError as e:
    return e
  applySchemaDefaults(unit['params']).validate(instance)
  return instance


def get_data_type_by_name(name):
  '''
  For a given name, get a datatype.
  For example this is used to get the datastore instance
  used by the handler based on the config in the unit.
  :param name: String the datastore's classname
  :return: The class
  '''
  return getattr(sys.modules[__name__], name)


class Threader(object):
  '''
  A basic thread manager that I reuse so much
  I should just polish it up and throw it into PyPI.
  More or less lets you run a "runnable" in a thread
  while something meaningful is happening in the main
  thread and kills it when complete.  I usually use it
  for things like API persistence on unrully/expirary
  endpoints that I don't want my interact logic to
  have to constantly poll something.  i.e.:
  ```
  def maintain_connection_to_some_api():
    while not amConnectedToSomeAPI:
      client = connectBackToTheStoopidThing(with_these,credentials)
  with Threader(maintain_connection_to_some_api) as API:
    API.client("don't worry")
    API.client("be happy")
  ```
  after the last `API.client()` call in that example,
  `maintain_connection_to_some_api()` is reaped silently.
  '''

  import time
  import threading
  method  = None
  args    = None
  thread  = None

  def __init__(self,method,args=None):
    '''
    Constructor
    :param method: Runnable function to call
    :param args: Tuple options args to pass
    '''
    self.method = method
    self.args = args

  def start(self):
    '''
    Start the thread
    :return: Bool whether the thread is still alive
    '''
    if self.args == None:
      self.thread = self.threading.Thread(target=self.method)
    else:
      assert type(self.args) == type(set())
      self.thread = self.threading.Thread(target=self.method,args=self.args)
    self.thread.daemon = True
    self.thread.start()
    assert self.thread.isAlive()
    return(self.thread.isAlive())

  def isAlive(self):
    '''
    Check to see if the thread is alive still.
    :return: Bool whether or not it is
    '''
    return self.thread.isAlive()

  def stop(self):
    '''
    Stop the thread
    :return: Bool if the assertion passes of course ;)
    '''
    self.thread._Thread__stop()
    assert not self.thread.isAlive()
    return(True)

  def __enter__(self):
    '''
    This is why I love python ;)
    :return: The threader instance itself
    '''
    self.start()
    return self

  def __exit__(self,type,value,traceback):
    '''
    Stop the thread upon exiting the `with` statement.
    :param type: who
    :param value: cares
    :param traceback: not
    :return: using
    '''
    self.stop()


class OpenThread(Threader):
  '''
  Same as above, but lets a thread keep running
  after exiting the `with` statement.
  '''
  def __exit__(self,type,value,traceback):
    pass