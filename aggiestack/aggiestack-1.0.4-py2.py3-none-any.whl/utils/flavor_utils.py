import connect_db
import logger
import os.path

import database

def loadFlavorList(flavorListPath):
    database.loadList(flavorListPath,["flavor_name","RAM","numDisks","numVcpus"],'flavor_collection')

def getFlavorList():
    print ("These are the flavors configured on the server")
    database.getList('flavor_collection')  

def getFlavor(flavor):
    return database.getItem('flavor_name',flavor,'flavor_collection')


def clearFlavorList():
    database.clearList('flavor_collection')

def isValidFlavor(flavor):
    return database.isAvailable('flavor_name',flavor,'flavor_collection')