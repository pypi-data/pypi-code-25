#!/usr/bin/env python

class Worker(object):
  '''
  A generic worker
  '''
  import zmq
  import cloud
  import time
  import pickle

  socket_type = zmq.REP

  worker_connection_uri = None
  running = True

  def __init__(self, worker_connection_uri, *args):
    '''
    Constructor
    :param worker_connection_uri: String zmq socket uri
    '''
    self.worker_connection_uri = worker_connection_uri
    self._context = self.zmq.Context()
    self._socket = self._context.socket(self.socket_type)
    self.setup_args(args)

  def setup_args(self, args):
    '''
    Not used here, but useful for more verbose workers
    :param args:
    :return:
    '''

  def start(self):
    '''
    Bind the worker socket and wait for work
    '''
    self._socket.bind(self.worker_connection_uri)
    while self.running:
      runnable_string = self._socket.recv_pyobj()
      runnable = self.pickle.loads(runnable_string)
      self._socket.send_pyobj('')
      args = self._socket.recv_pyobj()
      self._socket.send_pyobj('')
      kwargs = self._socket.recv_pyobj()
      response = self._do_work(runnable, args, kwargs)
      self._socket.send_pyobj(response)

  def stop(self):
    '''
    Stop the private main loop logically
    :return:
    '''
    self.running = False

  def _do_work(self, runnable, args, kwargs):
    '''
    Perform recieved work from a recently unmarshalled runnable.
    :param task: Runnable the work to do
    :return:
    '''
    print('Running [{}] with args [{}] and kwargs [{}]'.format(runnable, args, kwargs))
    return runnable(self, *args, **kwargs)