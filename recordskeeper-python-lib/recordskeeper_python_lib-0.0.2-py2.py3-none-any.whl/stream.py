"""Library to work with RecordsKeeper streams.

   You can publish, retrieve and verify stream data by using stream class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json and HTTPBasicAuth packages"""
	
import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import binascii
from recordskeeper_python_lib import *

""" Entry point for accessing Stream class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)

url = cfg['testnet']['url']
user = cfg['testnet']['rkuser']
password = cfg['testnet']['passwd']
chain = cfg['testnet']['chain']


"""Stream class to access stream related functions"""

class Stream:
	
	"""function to publish data into the stream"""

	def publish(address, stream, key, data):				#publish function definition
		
		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "publishfrom",
		          "params": [address,stream,key,data.encode('utf-8'). hex()],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		txid = response_json[0]['result']
		
		return txid;
	
	#txid = publish(address, stream, key, data.encode('utf-8'). hex() )		#variable to store transaction id

	
	"""function to retrieve data against transaction id from the stream"""

	def retrieve(stream, txid):								#retrieve() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "getstreamitem",
		          "params": [stream, txid],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		data = response_json[0]['result']['data']
		
		raw_data = binascii.unhexlify(data).decode('utf-8')		#returns raw data 
		
		return raw_data;

	#result = retrieve("root", "eef0c0c191e663409169db0972cc75ff91e577a072289ee02511b410bc304d90")						#call to invoke retrieve function
	

	"""function to retrieve data against a particular publisher address"""

	def retrieveWithAddress(stream, address):				#retrievewithAddress() function definition

		headers = { 'content-type': 'application/json'}
				
		payload = [
		{ "method": "liststreampublisheritems",
		"params": [stream, address],
		"jsonrpc": "2.0",
		"id": "curltext",
		"chain_name": chain
		}]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		key = response_json[0]['result'][0]['key']				#returns key value of the published data
		data = response_json[0]['result'][0]['data']			#returns published data
		txid = response_json[0]['result'][0]['txid']			#returns transaction id of the published data

		raw_data = binascii.unhexlify(data).decode('utf-8')		#returns raw data 

		return key, raw_data, txid;

	#key, raw_data, txid = retrieveWithAddress(stream, address)			#call to retrieveWithAddress() function


	"""function to retrieve data against a particular key value"""

	def retrieveWithKey(stream, key):					#retrieveithkey() function definition

		headers = { 'content-type': 'application/json'}
				
		payload = [
		{ "method": "liststreamkeyitems",
		"params": [stream, key],
		"jsonrpc": "2.0",
		"id": "curltext",
		"chain_name": chain
		}]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		publisher = response_json[0]['result'][0]['publishers'][0]		#returns publisher's address of published data		
		data = response_json[0]['result'][0]['data']					#returns published data
		txid = response_json[0]['result'][0]['txid']					#returns transaction id of published data

		raw_data = binascii.unhexlify(data).decode('utf-8')				#returns data published

		return publisher, raw_data, txid;

	#publisher, raw_data, txid = retrieveWithKey(stream, key)		#call to retrieveWithKey() function
	

	"""function to verify data on RecordsKeeper Blockchain"""

	def verifyData(stream, data, count):				#verifyData() function definition

		headers = { 'content-type': 'application/json'}
				
		payload = [
		{ "method": "liststreamitems",
		"params": [stream, False , count],
		"jsonrpc": "2.0",
		"id": "curltext",
		"chain_name": chain
		}]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		raw_data = []											

		for i in range(0, count):	
			
			result_data = response_json[0]['result'][i]['data']						#returns hex data

			if type(result_data) is str:

				raw_data.append(binascii.unhexlify(result_data).decode('utf-8'))	#returns raw data
				
			else:
					
				raw_data.append("No data found")		

		if data in raw_data:

			result = "Data is successfully verified."
				
		else:

			result = "Data not found."

		return result;

	#pub = verifyData("root","test data to check", 20 )		#call to verifyData() function

	"""function to list stream items on RecordsKeeper Blockchain"""

	def retrieveItems(stream, count):				#retrieveItems() function definition

		headers = { 'content-type': 'application/json'}
				
		payload = [
		{ "method": "liststreamitems",
		"params": [stream, False , count],
		"jsonrpc": "2.0",
		"id": "curltext",
		"chain_name": chain
		}]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()										

		address =[]
		key_value = []
		raw_data = []
		txid = []

		for i in range(0, count):	
			
			address.append(response_json[0]['result'][i]['publishers'])		#returns publisher address		
			key_value.append(response_json[0]['result'][i]['key'])			#returns key value of data
			data = response_json[0]['result'][i]['data']					#returns hex data
			raw_data = binascii.unhexlify(data).decode('utf-8')  			#returns raw data
			txid = response_json[0]['result'][i]['txid']					#returns tx id

		return address, key_value, raw_data, txid;

	#result = retrieveItems("root", 5)		#call to retrieveItems() function
