#!/usr/bin/env python
from .manager import *
from .utils import *



class Client(Manager):
  '''
  Handles RPC between the shell (or any other) and the manager
  '''
  import zmq
  manager_socket_type = zmq.REQ

  def __init__(self, *args):
    '''
    Constructor
    :param args: manager args
    '''
    self._context = self.zmq.Context()
    self._socket = self._context.socket(self.socket_type)
    self.setup_args(args)
    self._socket.linger = 30*1000

  def request(self, payload, timeout=10):
    '''
    Handles the round trip of the payload to the manager and back
    :param payload:
    :return: Manager response
    '''
    timeout = timeout*1000
    self._socket.connect(self.manager_uri)
    debug(payload, 'Sending payload to manager')
    self._socket.send_json(payload)
    poller = self.zmq.Poller()
    poller.register(self._socket, self.zmq.POLLIN)
    if poller.poll(timeout):
      debug(payload, 'Sending request to manager')
      response = self._socket.recv_json()
      debug(response, 'Response from manager')
      return response
    else:
      debug('Poller timed out')
      return client_message('Client request to manager timed out after {} seconds'.format(timeout/1000), level=1)
