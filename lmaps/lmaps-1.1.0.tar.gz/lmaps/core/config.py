#!/usr/bin/env python
import os
import yaml
from jsonschema import Draft4Validator, validators, validate, ValidationError

## TODO: Implement `.d` unit config loading

def extend_with_default(validator_class):
  '''
  Handles applying default values to schemas
  :param validator_class: Draft version class to validate with
  :return: Wrapped validator
  '''
  validate_properties = validator_class.VALIDATORS["properties"]
  def set_defaults(validator, properties, instance, schema):
    for property, subschema in properties.iteritems():
      if "default" in subschema:
        instance.setdefault(property, subschema["default"])
    for error in validate_properties(validator, properties, instance, schema):
      yield error
  return validators.extend(
    validator_class, {"properties": set_defaults},
  )
applySchemaDefaults = extend_with_default(Draft4Validator)


## Schema for the base configuration
config_schema = {
  "title": "lMaPS Service Configuration",
  "type": "object",
  "properties": {
    "rpc": {
      "type": "object",
      "default": {
        "manager_bind": "ipc:///run/lmaps_manager.sock",
        "worker_bind": "ipc:///run/lmaps_worker.sock"
      },
      "required": [
        "manager_bind",
      ],
      "properties": {
        "timeout": {
          "type": "integer",
          "default": 5*60
        },
        "manager_bind": {
          "type": "string",
          "pattern": "(tcp://.*:[0-9]+|ipc://.*|(pgm|epgm)://.*:.*:[0-9]+|inproc://.*)",
          "default": "ipc:///run/lmaps_manager.sock"
        },
        "worker_bind": {
          "type": "string",
          "pattern": "(tcp://.*:[0-9]+|ipc://.*|(pgm|epgm)://.*:.*:[0-9]+|inproc://.*)",
          "default": "ipc:///run/lmaps_worker.sock"
        }
      }
    },
    "units": {
      "type": "array",
      "default": [],
      "items":{
        "type": "object",
        "required": ["meta","handler","params"],
        "properties": {
          "meta": {
            "type": "object",
            "required": [
              "name"
            ],
            "properties": {
              "name": {
                "type": "string"
              },
              "store_root": {
                "type": "string"
              },
              "store_key": {
                "type": "string"
              }
            }
          },
          "handler": {
            "type": "object",
            "default": {
              "args": {}
            },
            "required": [
              "name",
              "type",
              "args"
            ],
            "properties": {
              "name": {
                "type": "string"
              },
              "type": {
                "type": "string"
              },
              "args": {
                "type": "object"
              }
            }
          },
          "params": {
            "type": "object"
          }
        }
      }
    }
  }
}

## Canidate filenames for the base config
config_names = [
  'lmaps.yaml',
  '.lmaps',
  '.lmaps.yaml'
]

## Canidate filepaths for the base configs
config_paths = [
  os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
  os.path.expanduser('~'),
  os.path.join(os.path.expanduser('~'), '.config'),
  '/etc',
  '/etc/lmaps',
]

def find_config_file():
  '''
  Use the list of paths and files above to find a config to use
  :return: Filepath of config file
  '''
  for path in config_paths:
    for name in config_names:
      if os.path.isfile(os.path.join(path,name)):
        return os.path.join(path,name)

def load_config(config_file = find_config_file()):
  '''
  Load the config as a dict from a given config file
  :param config_file: Path to config file
  :return: Dict containing the config
  '''
  try: assert not config_file == None
  except: raise Exception('Could not find a config file')
  with open(config_file, 'r') as f: config = yaml.load(f.read())
  validate(config, config_schema)
  applySchemaDefaults(config_schema).validate(config)
  return config
