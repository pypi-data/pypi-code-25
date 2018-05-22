#!/usr/bin/env python
'''
  A basic example of running an ansible playbook as the unit type.
Since the arguments of the config are not validated (IoC reasons)
at runtime, a schema needs to be declared here so that the unit
can be validated.  ALL plugins will need some schema declared
so that the handler can make sure what is being asked is valid.

The bare minimum is:
```
args_schema = {}
```
 to validate the unit config:
```
handler:
  name: some_name
  type: the_name_of_this_file_minus_the_py
  args:
    whatever: you put here
    gets: validated by
    args_schema: declared in the plugin
```

  If a plugin needs to hand instance operations (as this example does)
there needs to be `instance_create`, `instance_delete` and `instance_apply`
hook functions declared that can pass UnitHandler kwargs to your handler class.

  Upon construction, the instance can be had in `kwargs['instance']`
and the unit can be had in `kwargs['unit']`.  The instance gives you
the "what", the unit gives you the "where", and you just need to supply the "how".

  Once you get to the point where you need an actual "something" to occur, work can
be dispatched and received from `self.runner` in your UnitHandler.
'''

import os
import json
import yaml
import tempfile
import commands
from lmaps.core.tasks import *
from lmaps.core.utils import *
from lmaps.core.handlers import Handler

## This handler's schema
args_schema = {
  "required": [
    "playbook"
  ],
  "properties":
    {
      "playbook": {
        "type": "string"
      }
    }
}


## Runnable to send to workers to run the ansible-playbook command
def run_playbook(*args, **kwargs):
  '''
  Runs a playbook on a worker
  :param args: args
  :param kwargs: kwargs
  :return:
  '''
  cmd = 'ansible-playbook "{}" --extra-vars="@{}"'.format(kwargs['playbook'], kwargs['varfile'])
  try:
    results = commands.getstatusoutput(cmd)
  except:
    raise Exception('Error when attempting to run {}'.format(cmd))
  return results


class AnsiblePlaybook(Handler):
  '''
  Handles ansible-playbook type units
  '''
  playbook = None
  varfile  = None
  results  = None

  def setup(self):
    '''
    Configure this handler
    :return:
    '''
    self.instance = self.kwargs['instance']
    self.data = get_data_type_by_name(self.kwargs['unit']['meta']['data_type'])(
      store_root = self.kwargs['unit']['meta']['store_root'],
      store_key = self.kwargs['unit']['meta']['store_key']
    )
    self.playbook = self.kwargs['unit']['handler']['args']['playbook']
    self.preflight_checks()

  def create(self):
    '''
    Handles when a client wants to "create" an instance
    :return: Boolean the fact that it was created (exceptions get propagated back to the clients)
    '''
    if not self.data.exists(self.instance):
      self.data.new_store(self.instance)
    self.write_varsfile()
    return True

  def apply(self):
    '''
    Handles when a client wants to "apply" an instance
    :return: Boolean the fact that it was created (exceptions get propagated back to the clients)
    '''
    self.write_varsfile()
    try:
      self.results = self.runner(run_playbook, playbook=self.playbook, varfile=self.varfile)
    except Exception as e:
      raise Exception('Error dispatching ansible-playbook command\n\n{}'.format(str(e)))
    return True

  def preflight_checks(self):
    '''
    Makes sure things are all good before trying to use this handler
    '''
    try: assert os.path.isfile(self.playbook)
    except: raise Exception('Cannot find the playbook file "{}"'.format(self.playbook))

  def write_varsfile(self):
    '''
    Write the instance to an ansible vars file.
    :return: Tempfile handle/anchor/link/cursor/semaphore/refint/ioctl/whatever
    '''
    handle, filename = tempfile.mkstemp()
    with open(filename, 'w') as f:
      f.write(json.dumps(self.data.state(), indent=2))
    self.varfile = filename
    return self.varfile


def instance_create(**kwargs):
  '''
  This is the main incoming hook from the Manager Handler wanting a "create" to occur
  :return: A message for the client
  '''
  ansible_playbook = AnsiblePlaybook(**kwargs)
  try:
    ansible_playbook.create()
    return client_message("Instance created", extra=ansible_playbook.data.state())
  except:
    raise Exception('Could not create instance when attempting "ansible_playbook.create()"')

def instance_apply(**kwargs):
  '''
  This is the main incoming hook from the Manager Handler wanting an "apply" to occur
  :return: A message for the client
  '''
  ansible_playbook = AnsiblePlaybook(**kwargs)
  try:
    ansible_playbook.apply()
    return client_message(
      ansible_playbook.results[-1],
      level=ansible_playbook.results[0]
    )
  except:
    raise Exception('Could not apply instance(s) when attempting "ansible_playbook.apply()"')

def instance_delete(**kwargs):
  '''
  This is unsopperted at the moment
  :return: A message for the client
  '''
  raise Exception('Deletes are not supported by this plugin')
