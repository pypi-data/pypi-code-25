"""Library to work with RecordsKeeper Blockchain.

   You can retrieve blockchain information, node's information, node's balance, node's permissions, pending transaction details
   by using Blockchain class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii
from recordskeeper_python_lib import *

""" Entry point for accessing Blockchain class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)

url = cfg['testnet']['url']
user = cfg['testnet']['rkuser']
password = cfg['testnet']['passwd']
chain = cfg['testnet']['chain']


#Blockchain class to access blockchain related functions
class Blockchain:

	"""function to retrieve RecordsKeeper Blockchain parameters"""

	def getChainInfo():								#getChainInfo() function definition
		
		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "getblockchainparams",
		          "params": [],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		chain_protocol = result['chain-protocol']
		chain_description = result['chain-description']
		root_stream = result['root-stream-name']
		max_blocksize = result['maximum-block-size']
		default_networkport = result['default-network-port']
		default_rpcport = result['default-rpc-port']
		mining_diversity = result['mining-diversity']
		chain_name = result['chain-name']

		return chain_protocol, chain_description, root_stream, max_blocksize, default_networkport, default_rpcport, mining_diversity, chain_name;										#returns chain parameters

	#chain = getChainInfo()				 			#call to function getChainInfo()	


	"""function to retrieve node's information on RecordsKeeper Blockchain"""

	def getNodeInfo():								#getNodeInfo() function definition

		headers = { 'content-type': 'application/json'}

		payload = [

		 	{ "method": "getinfo",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		node_balance = response_json[0]['result']['balance']
		synced_blocks = response_json[0]['result']['blocks']
		node_address = response_json[0]['result']['nodeaddress']
		difficulty = response_json[0]['result']['difficulty']

		return node_balance, synced_blocks, node_address, difficulty;			#returns node details

	#node = getNodeInfo(public_address)		#getNodeInfo() function call


	"""function to retrieve node's permissions on RecordsKeeper Blockchain"""

	def permissions():							#permissions() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "listpermissions",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		
		pms_count = len(response_json[0]['result'])
		
		permissions = []

		for i in range(0, pms_count):
			permissions.append(response_json[0]['result'][i]['type'])

		return permissions;							#returns list of permissions

	#result = permissions()							#permissions() function call


	"""function to retrieve pending transactions information on RecordsKeeper Blockchain"""

	def getpendingTransactions():						#getpendingTransactions() function call

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getmempoolinfo",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		tx_count = response_json[0]['result']['size']		#store pending tx count

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getrawmempool",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response2 = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json2 = response2.json()
			
		tx = []

		for i in range(0, tx_count):
			tx.append(response_json2[0]['result'])
		
		return tx_count, tx;					#returns pending tx and tx count

	#pendingtx, pendingtxcount = getpendingTransactions()		#getpendingTransactions() function call


	"""function to check node's total balance """

	def checkNodeBalance():							#checkNodeBalance() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getmultibalances",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		balance = response_json[0]['result']['total'][0]['qty']

		return balance;							#returns balance of complete node

	#node_balance = checkNodeBalance()		#checkNodeBalance() function call

	
	

