import json
import os
from random import randint

def generate_ws_addr(ip, port):
  # todo: add checks
  return 'ws://' + ip + ':' + str(port)

def get_abi(abi_filepath=None):
  if not abi_filepath:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    abi_dir = os.path.join(current_dir, os.pardir)
    abi_filepath = os.path.join(abi_dir, 'contracts_data.json')
  with open(abi_filepath) as data_file:
    data = json.load(data_file)
  return data


def generate_nonce():
  return randint(0, 65534)