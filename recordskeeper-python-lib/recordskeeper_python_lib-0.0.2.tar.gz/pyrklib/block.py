"""Library to work with RecordsKeeper blocks.

   You can retrieve complete block information by using block class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json and HTTPBasicAuth packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
from recordskeeper_python_lib import *


""" Entry point for accessing Block class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)

url = cfg['testnet']['url']
user = cfg['testnet']['rkuser']
password = cfg['testnet']['passwd']
chain = cfg['testnet']['chain']


"""Block class to access block information"""

class Block:
	
	"""function to get a particular block"""

	def blockinfo(block_height):											#blockinfo function definition
		
		headers = { 'content-type': 'application/json'}
		
		payload = [
		         { "method": "getblock",
		          "params": [block_height],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		tx_count = len(response_json[0]['result']['tx'])					#variable returns block's transaction count
		miner = response_json[0]['result']['miner']							#variable returns block's miner 
		size = response_json[0]['result']['size']							#variable returns block's size
		nonce = response_json[0]['result']['nonce']							#variable returns block's nonce
		blockHash = response_json[0]['result']['hash']						#variable returns blockhash
		prevblock = response_json[0]['result']['previousblockhash']			#variable returns prevblockhash
		nextblock = response_json[0]['result']['nextblockhash']				#variable returns nextblockhash
		merkleroot = response_json[0]['result']['merkleroot']				#variable returns merkleroot
		blocktime = response_json[0]['result']['time']						#variable returns blocktime
		difficulty = response_json[0]['result']['difficulty']				#variable returns difficulty

		tx = []																#list to store transaction ids
		
		for i in range(0, tx_count):
			
			tx.append(response_json[0]['result']['tx'][i])					#appends transaction ids into tx list
			


		return  tx_count, tx, miner, size, nonce, blockHash, prevblock, nextblock, merkleroot, blocktime, difficulty;

	
	#tx_count, tx, miner, size, nonce, blockHash, prevblock, nextblock, merkleroot, blocktime, difficulty = blockinfo("100")		#call to blockinfo function 


	"""function to retrieve blocks on RecordsKeeper Blockchain"""

	def retrieveBlocks(block_range):		#retrieveBlocks() function definition
		
		blockhash = []
		miner = []
		blocktime = []
		tx_count = []

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "listblocks",
		          "params": [block_range],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		block_count = len(response_json[0]['result'])

		for i in range(0, block_count):

			blockhash.append(response_json[0]['result'][i]['hash'])
			miner.append(response_json[0]['result'][i]['miner'])
			blocktime.append(response_json[0]['result'][i]['time'])
			tx_count.append(response_json[0]['result'][i]['txcount'])
		
		return blockhash, miner, blocktime, tx_count;				

	
	#block_hash, miner_add, block_time, txcount = retrieveBlocks("10-15")	#call to function retrieveBlocks

