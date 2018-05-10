"""Library to work with RecordsKeeper Blockchain permissions.

   You can grant and revoke permissions to any node on Recordskeeper Blockchain by using permissions class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii
from recordskeeper_python_lib import *

""" Entry point for accessing Permissions class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)

url = cfg['testnet']['url']
user = cfg['testnet']['rkuser']
password = cfg['testnet']['passwd']
chain = cfg['testnet']['chain']


#Permissions class to access blockchain related functions
class Permissions:

	"""function to grant permissions on RecordsKeeper Blockchain"""

	def grantPermission(address, permissions):			#grantPermission() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "grant",
		          "params": [address, permissions],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = response_json[0]['error']['message']

		else:

			res = response_json[0]['result']
			
		return res;									#returns permissions tx id

	#txid = grantPermission(address, permissions)		#call to function grantPermission()	


	"""function to revoke permissions on RecordsKeeper Blockchain"""

	def revokePermission(address, permissions):		#revokePermission() function definition


		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "revoke",
		      "params": [address, permissions],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = response_json[0]['error']['message']

		else:

			res = response_json[0]['result']

		return res;									#returns revoke permissions tx id

	#txid = revokePermission(address, permissions)		#revokePermission() function call