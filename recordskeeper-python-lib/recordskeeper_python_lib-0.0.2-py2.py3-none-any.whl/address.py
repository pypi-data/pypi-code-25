"""Library to work with RecordsKeeper address class.

   You can generate new address, check all addresses, check address validity, check address permissions, check address balance
   by using Address class. You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii
from recordskeeper_python_lib import *

""" Entry point for accessing Address class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)


url = cfg['testnet']['url']
user = cfg['testnet']['rkuser']
password = cfg['testnet']['passwd']
chain = cfg['testnet']['chain']


#Address class to access address related functions
class Address:


	"""function to generate new address on the node's wallet"""

	def getAddress():									#getAddress() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getnewaddress",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		address = response_json[0]['result']

		return address;									#returns new address

	#newAddress = getAddress()							#getAddress() function call

	"""function to generate a new multisignature address"""

	def getMultisigAddress(nrequired, key):				#getMultisigAddress() function definition

		key_list = key.split(",")

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "createmultisig",
		      "params": [nrequired, key_list],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		address = response_json[0]['result']

		if address is None:

			res = response_json[0]['error']['message']

		else:

			res = response_json[0]['result']['address']

		return res;										#returns new multisig address

	#newAddress = getMultisigAddress(nrequired, key)	#getMultisigAddress() function call


	"""function to generate a new multisignature address on the node's wallet"""

	def getMultisigWalletAddress(nrequired, key):		#getMultisigWalletAddress() function definition

		key_list = key.split(",")

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "addmultisigaddress",
		      "params": [nrequired, key_list],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		
		address = response_json[0]['result']

		if address is None:

			res = response_json[0]['error']['message']

		else:

			res = response_json[0]['result']

		return res;									#returns new multisig address

	#newAddress = getMultisigWalletAddress(nrequired, key)	#getMultisigWalletAddress() function call
	

	"""function to list all addresses and no of addresses on the node's wallet"""


	def retrieveAddresses():						#retrieveAddresses() function call

		headers = { 'content-type': 'application/json'}

		payload = [

		 	{ "method": "getaddresses",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		
		address_count = len(response_json[0]['result'])

		address = []

		for i in range(0, address_count):
			
			address.append(response_json[0]['result'][i])

		return address, address_count;					#returns allAddresses and address count

	#allAddresses, address_count = retrieveAddresses()	#retrieveAddresses() function call


	"""function to check if given address is valid or not"""

	def checkifValid(address):						#checkifValid() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "validateaddress",
		      "params": [address],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		validity = response_json[0]['result']['isvalid']

		
		if validity is True:
			addressCheck = "Address is valid"		#print if address is valid

		else:
			addressCheck= "Address is invalid"		#print if address is invalid	

		return addressCheck;						#returns validity of address

	#addressC = checkifValid(address)				#checkifValid() function call


	"""function to check if given address has mining permission or not"""


	def checkifMineAllowed(address):				#checkifMineAllowed() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "validateaddress",
		      "params": [address],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		permission = response_json[0]['result']['ismine']


		if permission is True:
			
			permissionCheck = "Address has mining permission"	#print if address has mining permission

		else:
			
			permissionCheck = "Address has not given mining permission"	#print if address does not have mining permission	

		return permissionCheck;							#returns mining permission

	#permissionCheck = checkifMineAllowed(address)	#checkifMineAllowed() function call
	

	"""function to check node address balance on RecordsKeeper Blockchain"""

	def checkBalance(address):					#checkBalance() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getaddressbalances",
		      "params": [address],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		balance = response_json[0]['result'][0]['qty']

		return balance;							#returns balance of a particular node address

	#address_balance = checkBalance(address)	#checkBalance() function call
	

	"""function to import address on RecordsKeeper Blockchain"""

	def importAddress(public_address):				#importAddress() function call

		headers = { 'content-type': 'application/json'}
		payload = [
		    { "method": "importaddress",
		      "params": [public_address, " ", False],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']
		error = response_json[0]['error']

		if result is None and error is None:
			
			resp = "Address successfully imported"

		elif (result is None and error != None):

			resp = response_json[0]['error']['message']			#returns new multisig address
		
		else:

			resp = 0

		return resp;

	#import_address = importAddress("msCM5qQ32Tjc1ydEN1rpoJy4h3qxNPXU15")	#importAddress() function call