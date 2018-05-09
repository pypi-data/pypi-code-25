import requests
import json
from .azure_token import getAccessKey
from xml.etree import ElementTree

class Operation:
	def __init__(self, name, env, http, pcfEndPoint, apimEndPoint, apimPath):
		self.name = name
		self.env = env
		self.http = http
		self.pcfEndPoint = pcfEndPoint
		self.apimEndPoint = apimEndPoint
		self.apimPath = apimPath


def getApis(apim):
	apim.token = getAccessKey(apim.apimId, apim.apimKey)

	requestUrl = "apis"
	headers = {"Content-Type": "application/json",
					"Authorization" : apim.token}

	myResponse = requests.get(apim.apimBaseUrl + requestUrl, headers=headers, params=apim.apiVersion, json={})
	return myResponse.json()

def getApi(apim, apiName):
	data = getApis(apim)
	for item in data['value']:
		if item['name'] == apiName:
			return item
	return None


def getOperations(apim, id):
	apim.token = getAccessKey(apim.apimId, apim.apimKey)

	requestUrl = id + "/operations"
	headers = {"Content-Type": "application/json",
					"Authorization" : apim.token}

	myResponse = requests.get(apim.apimBaseUrl + requestUrl, headers=headers, params=apim.apiVersion, json={})
	return myResponse.json()



def getPolicy(apim, id):
	if apim.token is None:
		apim.token =getAccessKey(apim.apimId, apim.apimKey)

	requestUrl = id + "/policy"
	headers = {"Content-Type": "application/xml",
					"Authorization" : apim.token}

	myResponse = requests.get(apim.apimBaseUrl + requestUrl, headers=headers, params=apim.apiVersion, json={})
	return myResponse


def getRewriteUrl(apim, id):
	response = getPolicy(apim, id)
	tree = ElementTree.fromstring(response.content)
	for backend in tree.iter('rewrite-uri'):
		try:
			return backend.attrib['template']
		except:
			return None
	


def updateSubscriptionKeyParameterNames(apim, apiName):
	api = getApi(apim, apiName)
	if api is None:
		return None

	requestUrl = api['id']
	headers = {"Content-Type": "application/json",
					"Authorization" : apim.token,
					"If-Match": "*"}

	body = {
				"subscriptionKeyParameterNames":
			    {
	 		       "header": "Application-Id",
	  		       "query": "subscription-key"
  				}
			}

	myResponse = requests.patch(apim.apimBaseUrl + requestUrl[1:], headers=headers, params=apim.apiVersion, json=body)
	return myResponse


def updateUrlTemplate(apim, operation, apimURL):
	requestUrl = operation['id']

	headers = {"Content-Type": "application/json",
					"Authorization" : apim.token,
					"If-Match": "*"}

	body = {
		"urlTemplate": apimURL
	}
	myResponse = requests.patch(apim.apimBaseUrl + requestUrl[1:], headers=headers, params=apim.apiVersion, json=body)
	return myResponse


def updateRewriteUrl(operation, rewriteUrl):
	print("Hello")







