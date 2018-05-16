import requests
from .helpers import *
from .constants import *

def getGroups(apim):
	requestUrl = "groups"
	return simpleGet(apim, requestUrl)

def getGroupsDictionary(apim):
	groups = getGroups(apim)
	return buildNameAndIdDictionary(groups)

def createGroup(apim, name):
	headers = basicPutPatchHeader(apim)
	body = {
			"name": name,
			"description": "Created by azure_helper",
			"builtIn": "false",
			"type": "custom",
			"externalId": "null"
		}
	requestUrl = "groups/" + name
	myResponse = requests.put(apim.apimBaseUrl + requestUrl, headers=headers, json=body, params=apim.apiVersion)
	return myResponse

def getGroupUsers(apim, group):
	requestUrl = group + "/users"
	return simpleGet(apim, requestUrl)

def addUserToGroup(apim, group, user):
	headers = basicPutPatchHeader(apim)
	body = {
			"firstName": user.firstName,
			"lastName": user.lastName,
			"email": user.email
			}
	requestUrl = apim.apimBaseUrl + group.replace("/", "", 1) + user.userId
	return requests.put(requestUrl, headers=headers, json=body, params=apim.apiVersion)
