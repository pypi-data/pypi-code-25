"""Library to work with assets.

   You can issue assets or retrieve assets information by using asset class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json and HTTPBasicAuth packages"""
	
import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import binascii

""" Entry point for accessing Stream class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)

url = cfg['testnet']['url']
user = cfg['testnet']['rkuser']
password = cfg['testnet']['passwd']
chain = cfg['testnet']['chain']


"""Asset class to access asset related functions"""

class Asset:
	
	"""function to create or issue an asset"""

	def issue(address, asset_name, asset_qty):				#issue asset function definition
		
		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "issue",
		          "params": [address, asset_name, asset_qty],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		txid = response_json[0]['result']
		
		return txid;
	
	#txid = issue(address, asset_name, asset_qty)		#variable to store issue transaction id

	
	"""function to retrieve assets information"""

	def retrieveAssets():								#retrieveAssets() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "listassets",
		          "params": [],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		asset_count = len(response_json[0]['result'])					#returns assets count

		for i in range(0, asset_count):

			asset_name = response_json[0]['result'][i]['name']			#returns asset name
			issue_id = response_json[0]['result'][i]['issuetxid']		#returns issue id
			issue_qty = response_json[0]['result'][i]['issueraw']		#returns issue quantity
		
		return asset_name, asset_name, asset_qty, asset_count;

	#result = retrieveAssets()					#call to invoke retrieveAssets() function
	

	