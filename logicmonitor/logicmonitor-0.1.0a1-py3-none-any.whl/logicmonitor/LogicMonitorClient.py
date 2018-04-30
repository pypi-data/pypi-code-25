import requests
import json
import hashlib
import base64
import time
import hmac

class LogicMonitorClient:

	# Ctor
	def __init__(self, account, accessId, accessKey):
		self._account = account
		self._accessId = accessId
		self._accessKey = accessKey

	# toString()
	def toString(self):
		return '{0}: {1}'.format(self._account, self._accessId)

	# response()
	def response(self, httpVerb, resourcePath, queryParams, data):
		#Construct URL 
		url = 'https://{0}.logicmonitor.com/santaba/rest{1}{2}'.format(self._account, resourcePath, queryParams)

		# Get current time in milliseconds
		epoch = str(int(time.time() * 1000))
		# epoch = '1525088468757'

		#Concatenate Request details
		requestVars = '{0}{1}{2}{3}'.format(httpVerb, epoch, data, resourcePath)

		#Construct signature
		hmacObj = hmac.new(bytes(self._accessKey, 'utf-8'), msg=bytes(requestVars, 'utf-8'), digestmod=hashlib.sha256)
		digest = hmacObj.hexdigest()
		signature = base64.b64encode(bytes(digest, 'utf-8')).decode()

		#Construct headers
		auth = 'LMv1 {0}:{1}:{2}'.format(self._accessId, signature, epoch)
		headers = {
			'Content-Type':'application/json',
			'Authorization':auth,
			##'Accept':'application/octet-stream;application/json',
			##'X-Requested-With':'XMLHttpRequest',
			#'X-version':'1',
			#'X-CSRF-Token':'Fetch',
		}

		#Make request
		response = requests.get(url, data=data, headers=headers)

		return response

	# responseFile()
	def responseFile(self, httpVerb, resourcePath, queryParams, data, fileName):
		response = self.response(httpVerb, resourcePath, queryParams, data)
		if(response.status_code / 100 != 2):
			# Failure code
			raise ValueError('Failed to download.')
		# OK Status code

		# Write the result
		file = open(fileName, 'wb')
		for chunk in response.iter_content(100000):
			 file.write(chunk)
		file.close()

		return response

	"""
	HTTP GET
	:param resourcePath: The resource path
	:param queryParams: Optional query parameters
	"""
	def get(self, resourcePath, queryParams = ''):
		response = self.response('GET', resourcePath, queryParams, '')
		
		# Status code OK?
		if(200 != response.status_code):
			# No
			raise ValueError('Non-200 response code: {0}'.format(response.status_code))
		# Yes
		
		# Return the data node
		entity = json.loads(response.content)['data']
		return entity