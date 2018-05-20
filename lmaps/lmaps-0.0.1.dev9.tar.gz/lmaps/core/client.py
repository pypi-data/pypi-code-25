#!/usr/bin/env python
from .manager import *
from .utils import *

class Client(Manager):
  '''
  Handles RPC between the shell (or anyother) and the manager
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

  def request(self, payload):
    '''
    Handles the round trip of the payload to the manager and back
    :param payload:
    :return:
    '''
    self._socket.connect(self.manager_uri)
    self._socket.send_json(payload)
    return self._socket.recv_json()

