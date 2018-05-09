import requests
import json
from .azure_token import getAccessKey
from .constants import *


class AppIdList(object):
    def __init__(self, appIds):
        self.appIds = appIds

    def __contains__(self, appId):  # implements `in`
        return appId.lower() in (n.lower() for n in self.appIds)

    def add(self, appId):
        self.appIds.append(appId)


# Azure is case-insensitive, but the code is not. This func will allow you to pass in an app id of any case and get its value back as it was created in Azure
def getExactValueOfKey(myDict, value):
    newlist = list(myDict.keys())
    index = [n.lower() for n in newlist].index(value.lower())
    return newlist[index]


def refreshToken(apim):
    apim.token = getAccessKey(apim.apimId, apim.apimKey)


def simpleGet(apim, requestUrl):
    if apim.token is None:
        apim.token = getAccessKey(apim.apimId, apim.apimKey)
    headers = basicHeader(apim)
    myResponse = requests.get(apim.apimBaseUrl + requestUrl, headers=headers, params=apim.apiVersion, json={})

    return myResponse.json()


def buildNameAndIdDictionary(data):
    response = {}
    for item in data['value']:
        response[item['name']] = item['id']
    return response


def findIdByName(myDict, name):
    pass

def is_json(data):
    try:
        json_object = json.loads(data)
    except(ValueError):
        return False
    return True