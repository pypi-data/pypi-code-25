import json
from web3 import Web3, WebsocketProvider
import socket
import os

from python.test.helper import Helper

class Skale:
  def __init__(self, ip, port):
    ws_addr = Helper.generate_ws_addr(ip, port)
    self.init_web3(ws_addr)
    self.init_contracts()

  def init_contracts(self):
    abi_file =os.path.join(os.path.dirname(os.path.realpath(__file__)), 'contracts_data.json')
    with open(abi_file) as data_file:
      data = json.load(data_file)

    self.manager_addr = Web3.toChecksumAddress(data['node_manager_address'])
    self.manager_contract = self.web3.eth.contract(address=self.manager_addr, abi=data['node_manager_abi'])

    self.token_addr = Web3.toChecksumAddress(data['token_address'])
    self.token_contract = self.web3.eth.contract(address=self.token_addr, abi=data['token_abi'])

  def init_web3(self, ws_addr):
    self.web3 = Web3(WebsocketProvider(ws_addr))

  def create_node(self, ip, port, account):
    deposit_val = 100000000000000000000
    opts = {'from': self.web3.eth.accounts[0], 'gas': 1800000}
    type = 0x1
    nonce = 12345

    address = Web3.toChecksumAddress(account)[2:]
    data_params = type.to_bytes(1, byteorder='big') + \
                  port.to_bytes(4, byteorder='big') + \
                  nonce.to_bytes(4, byteorder='big') + \
                  socket.inet_aton(ip) + \
                  bytes.fromhex(address)

    return self.token_contract.functions.transfer(self.manager_addr, deposit_val, data_params).transact(opts)
