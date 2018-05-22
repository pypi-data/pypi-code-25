#!/usr/bin/env python
import os
import time
import yaml
from .utils import *
from lmaps.core.config import load_config


class DataStore(object):
  '''
  Base class that provides the actual structures used by handlers
  '''

  args = ()
  kwargs = {}

  def __init__(self, *args, **kwargs):
    '''
    Constructor
    '''
    self.args = args
    self.kwargs = kwargs
    self.setup()

  def setup(self):
    '''
    Prepare the instance
    :return:
    '''

  def new_store(self):
    '''
    Create a new store in which to put/get state
    :return: Pointer to the new store
    '''

  def state(self):
    '''
    Get the summary of the current state
    :return: Dict of state summary
    '''

  def exists(self, data):
    '''
    Check if a store already contains data
    :param data: Data to compare
    :return: Boolean as to whether or not it exists
    '''

  def rollback(self): pass


class YamlFile(DataStore):
  '''
  DataStore based on using merged YAML files to determine state
  '''

  store_root   = None
  store_key    = "root"
  current_dir  = "current"
  rollback_dir = "rollback"

  def setup(self):
    '''
    Setup this instance to work with yaml files
    '''
    self.store_root = self.kwargs['store_root']
    if 'store_key' in self.kwargs:
      self.store_key = self.kwargs['store_key']
    if not os.path.isdir(self.get_current_store_dir()):
      os.makedirs(self.get_current_store_dir())
    if not os.path.isdir(self.get_rollback_store_dir()):
      os.makedirs(self.get_rollback_store_dir())

  def get_current_store_dir(self):
    '''
    Get the filepath to the "current" data stores
    :return: String filepath
    '''
    return os.path.join(
      os.path.join(
        self.store_root,
        self.current_dir
      )
    )

  def get_rollback_store_dir(self):
    '''
    Get the filepath to the "rollback" data stores
    :return: String filepath
    '''
    return os.path.join(
      os.path.join(
        self.store_root,
        self.rollback_dir
      )
    )

  def store_files(self):
    '''
    Enumerate the "current" store's files
    :return: List of filepaths
    '''
    files = []
    for file in os.listdir(self.get_current_store_dir()):
      files.append(os.path.join(self.get_current_store_dir(),file))
    return files

  def new_store(self, data):
    '''
    Provision a new store
    :param data: Dict of instamce
    :return: String filepath
    '''
    store_file = os.path.join(self.get_current_store_dir(),str(time.time())+".yaml")
    with open(store_file, 'w') as f:
      f.write(yaml.dump(data))
    return store_file

  def state(self):
    '''
    Get the current summary of the state
    :return: Dict of state
    '''
    summary = {}
    for store_file in self.store_files():
      with open(store_file, 'r') as f:
        summary = dict(summary.items() + yaml.load(f.read()).items())
    return summary

  def exists(self, data):
    '''
    Check if data is already in a store based on a sample
    :param data:
    :return: Boolean as to whether or not the data is already in a store
    '''
    if data in self.state():
      return True
    else:
      return False

  def rollback(self):
    '''
    Rollback the latest change by moving the last store from the "current" directory to the "rollback" directory
    :return: Dict of the data rolled back
    '''
    files = self.store_files()
    if files == []:
      return files
    else:
      latest = files[-1]
      rollback_path = os.path.join(self.get_rollback_store_dir(),os.path.basename(latest))
      os.rename(latest, rollback_path)
      with open(rollback_path,'r') as f:
        return yaml.load(f.read())


class YamlList(YamlFile):
  '''
  DataStore based on using YAML files to present state as a list of dicts
  '''

  def state(self, reverse=False):
    '''
    Get the current summary of the state
    :param reverse: whether or not the state needs to be reversed
    :return: List of instances
    '''
    summary = []
    files = self.store_files()
    if reverse:
      files = reversed(files)
    for store_file in files:
      with open(store_file, 'r') as f:
        summary.append(yaml.load(f.read()))
    return summary

  def exists(self, data):
    '''
    Check if data is already in a store based on a sample
    :param data:
    :return: Boolean as to whether or not the data is already in a store
    '''
    if [data] in self.state():
      return True
    else:
      return False


class YamlKeyList(YamlList):
  '''
  DataStore based on using YAML files to present state as a dict of dicts
  '''

  def state(self, reverse=False):
    '''
    DataStore based on using YAML files to present state as a list of dicts
    '''
    summary = {self.store_key: []}
    files = self.store_files()
    if reverse:
      files = reversed(files)
    for store_file in files:
      with open(store_file, 'r') as f:
        summary[self.store_key].append(yaml.load(f.read()))
    return summary

  def exists(self, data):
    '''
    Check if data is already in a store based on a sample
    :param data:
    :return: Boolean as to whether or not the data is already in a store
    '''
    if data in self.state()[self.store_key]:
      return True
    else:
      return False

class YamlKeyDict(YamlKeyList):
  '''
  DataStore based on using YAML files to present state as a dict of dicts
  '''

  def state(self, reverse=False):
    '''
    DataStore based on using YAML files to present state as a merged dict
    '''
    summary = {self.store_key: {}}
    files = self.store_files()
    if reverse:
      files = reversed(files)
    for store_file in files:
      with open(store_file, 'r') as f:
        loaded = yaml.load(f.read())
      summary[self.store_key] = dict(loaded.items() + summary[self.store_key].items())
    return summary
