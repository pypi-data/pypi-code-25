import json
import os
from random import randint

def generate_ws_addr(ip, port):
  # todo: add checks
  return 'ws://' + ip + ':' + str(port)

def get_abi():
  current_dir = os.path.dirname(os.path.realpath(__file__))
  abi_dir = os.path.join(current_dir, os.pardir)
  abi_file = os.path.join(abi_dir, 'contracts_data.json')
  with open(abi_file) as data_file:
    data = json.load(data_file)
  return data


def generate_nonce():
  return randint(0, 65534)