import requests
from .helpers import AppIdList
from .constants import *
from .azure_token import getAccessKey

class Subscription:
    	# appId expects a dictionary in the form of Azure Product Name : Primary key to use for that product subscription
	# Need to revise appId to be dictionary: ?? "appid": ["subscription name", "product"]
	def __init__(self, primaryKey, userId, subscriptionId):
		self.primaryKey = primaryKey
		self.userId = userId
		self.subscriptionId = subscriptionId


def getSubscriptions(apim):
	apim.token = getAccessKey(apim.apimId, apim.apimKey)

	requestUrl = "subscriptions"
	headers = basicHeader(apim)
	
	myResponse = requests.get(apim.apimBaseUrl + requestUrl, headers=headers, params=apim.apiVersion, json={})

	return myResponse.json()

# Gets list of app ids with azure uid
def getConfiguredAppIds(data):
	appIds = {}
	for item in data['value']:
		appIds[item['primaryKey']] = Subscription(item['primaryKey'], item['userId'], item['id'])

	return appIds

# list of app ids as list object
def getOnlyAppIdsAsList(apim):
	data = getSubscriptions(apim)
	appIds =  getConfiguredAppIds(data)

	return AppIdList(appIds.keys())
	
def updateSubscription(apim, currentSubscription, body):
	headers = basicPutPatchHeader(apim)
	body = body
	requestUrl = currentSubscription.subscriptionId[1:]

	myResponse = requests.patch(apim.apimBaseUrl + requestUrl, headers=headers, json=body, params=apim.apiVersion)
	return myResponse

def deleteSubscription(apim, subscriptionId):
	headers = basicPutPatchHeader(apim)
	params = apim.apiVersion
	requestUrl = subscriptionId

	requests.delete(apim.apimBaseUrl + requestUrl, headers=headers, params=params)





def isAppIdConfigured(data, value):
	if value in data:
		return True
	else:
		return False

