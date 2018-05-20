import os
import yaml
import lmaps
from nose.tools import with_setup

global config
global config_filename
config = {}
config_filename = 'lmaps.test_config.yaml.tmp'
socket_filename = 'lmaps.test_socket.tmp'


def fake_runner(runnable, *args, **kwargs):
  print('runnable: {}'.format(str(runnable)))
  print('args:     {}'.format(str(args)))
  print('kwargs:   {}'.format(str(kwargs)))
  return runnable(*args, **kwargs)


def setup_configfile():
  with open(config_filename, 'w') as f: f.write(yaml.dump({"rpc":{"manager_bind":'ipc://'+socket_filename}}))
  config = lmaps.core.config.load_config(config_file = config_filename)
  return config


def teardown_configfile():
  if os.path.isfile(config_filename): os.remove(config_filename)
  if os.path.isfile(socket_filename): os.remove(socket_filename)


def test_config_schema():
  config_examples = [
    {},
    {"rpc": {"manager_bind": "ipc:///tmp/test"}},
    {"rpc": {"manager_bind": "tcp://localhost:1234"}},
    {"rpc": {"manager_bind": "tcp://127.0.0.1:1234"}},
    {"rpc": {"manager_bind": "tcp://*:1234"}},
    {"rpc": {"manager_bind": "tcp://::1:1234"}},
    {
      "units": [
        {
          "meta": {
            "name":"test",
            "primary_key": "test"
          },
          "handler": {
            "name": "test",
            "type": "test",
            "args": {}
          },
          "params": {}
        }
      ]
    }
  ]
  for config in config_examples:
    lmaps.core.config.applySchemaDefaults(lmaps.core.config.config_schema).validate(config)

@with_setup(setup_configfile, teardown_configfile)
def test_config_fileloader():
  pass

'''
@with_setup(setup_configfile, teardown_configfile)
def test_shell_start():
  class Args(object):
    daemon = False
    config_file = config_filename
  lmaps.core.shell.start(Args())
'''

@with_setup(setup_configfile, teardown_configfile)
def test_daemon_create_worker():
  from lmaps.core.daemon import Daemon
  return Daemon(config=setup_configfile())

@with_setup(setup_configfile, teardown_configfile)
def test_daemon_start_workers():
  daemon = test_daemon_create_worker()
  daemon.start_workers()

def test_ansible_playbook_run():
  from lmaps.plugins.ansible_playbook import run_playbook
  run_playbook(playbook="examples/tests/ansible_playbook/example.yaml", varfile="examples/tests/ansible_playbook/example.json")

def test_ansible_playbook_handler():
  from lmaps.plugins.ansible_playbook import AnsiblePlaybook
  from lmaps.core.manager import Manager
  manager = Manager('','')
  instance = {
    "foo": "baz"
  }
  unit = {
    "meta":{
      "data_type": "YamlKeyList",
      "store_root": "store_root.tmp",
      "store_key": "test",
    },
    "handler":{
      "args":{"playbook":"examples/tests/ansible_playbook/example.yaml"}
    }
  }
  a = AnsiblePlaybook(context=manager, runner=fake_runner, instance=instance, unit=unit)
