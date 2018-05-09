import requests
from .helpers import *
from .azure_token import getAccessKey


def getProducts(apim):
	requestUrl = "products"
	return simpleGet(apim, requestUrl)


def findProductIdByName(apim, productName):
	products = getProductsDictionary(apim)

	if productName in products:
		return products[productName]
	else:
		return None



def getProductsDictionary(apim):
	products = getProducts(apim)
	return buildNameAndIdDictionary(products)




		# Call the get products method then loop over and create dict of product name : product id


