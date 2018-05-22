#!/usr/bin/env python
import sys
import time
from .worker import Worker
from .manager import Manager
from .utils import *

class Daemon(object):
  '''
  Handles running various threads needed on the host
  '''
  config = {}
  workers = []
  threads = []
  def __init__(self, config):
    '''
    Constructor
    :param config: Dict of the config
    '''
    self.config = config
    self.make_workers()

  def run(self):
    '''
    Start the workers
    '''
    self.manage_workers()

  def manage_workers(self):
    '''
    Maintains the manager and worker threads
    '''
    self.start_workers()
    manager = Manager(self.config['rpc']['worker_bind'],self.config['rpc']['manager_bind'])
    manager.config = self.config
    with Threader(manager.start) as manager_thread:
      while True:
        time.sleep(1)
        for worker in self.threads:
          if not worker.isAlive():
            print('Restarting worker thread')
        if not manager_thread.isAlive():
          print('Restarting manager thread')
          manager_thread.start()

  def make_workers(self, count=1):
    '''
    Create workers
    :param count: Number of workers to create
    '''
    for i in range(count):
      worker = Worker(self.config['rpc']['worker_bind'])
      worker.config = self.config
      self.workers.append(worker)

  def start_workers(self):
    '''
    Start the workers in their own threads
    '''
    for worker in self.workers:
      with OpenThread(worker.start) as t:
        self.threads.append(t)
