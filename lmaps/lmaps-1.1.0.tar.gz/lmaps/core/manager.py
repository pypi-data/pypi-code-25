#!/usr/bin/env python
from .tasks import *
from .handlers import *
from .worker import Worker


class Manager(Worker):
  '''
  In charge of listening to clients and passing the requests to a handler
  '''

  import zmq
  socket_type = zmq.REQ
  manager_socket_type = zmq.REP

  schema = {
    "title": 'Lightweight Management and Provisioning Service',
    "properties": {
      "create": {
        "title": "Create an instance",
        "type": "boolean",
        "default": False
      },
      "apply": {
        "title": "Apply the instance(s)",
        "type": "boolean",
        "default": False
      },
      "rollback": {
        "title": "Remove the newest instance from the unit",
        "type": "boolean",
        "default": False
      },
      "unit": {
        "title": "Name of unit on which actions are performed",
        "type": "string",
        "default": None
      },
      "instance": {
        "title": "Yaml file with which to perform operations",
        "type": "string",
        "default": None
      },
      "list_units": {
        "title": "List units",
        "type": "boolean",
        "default": False
      },
      "show_summary": {
        "title": "Get the current summarized state of a unit",
        "type": "boolean",
        "default": False
      },
    }
  }

  def setup_args(self, args):
    '''
    Make sure we can connect to workers and bind our socket for clients
    :param args:
    :return:
    '''
    self.manager_uri = args[0]
    self._manager_context = self.zmq.Context()
    self._manager_socket = self._manager_context.socket(self.manager_socket_type)

  def start(self):
    '''
    Begin serving
    '''
    self._client_poller = self.zmq.Poller()
    self._client_poller.register(self._manager_socket, self.zmq.POLLIN)
    self._manager_socket.bind(self.manager_uri)
    self._socket.connect(self.worker_connection_uri)
    manager_handler = ManagerHandler(context=self, runner=self.run_task)
    while self.running:
      for poll in self._client_poller.poll(1000):
        socket = poll[0]
        request = socket.recv_json()
        self._manager_socket.send_json(
          manager_handler.client_request(request)
        )

  def run_task(self, runnable, *args, **kwargs):
    '''
    Takes a "runnable" method and args, marshalls them, and sends them
    to a worker via the worker socket.  After sending, this will wait
    for a response from the worker as the return from the runnable.
    :param runnable: An unbound method/function/whatever
    :return: return from the runnable that executed on the worker
    '''
    marshall_string = self.cloud.serialization.cloudpickle.dumps(runnable)
    for message in [marshall_string, args]:
      self._socket.send_pyobj(message)
      self._socket.recv()
    self._socket.send_pyobj(kwargs)
    return self._socket.recv_pyobj()