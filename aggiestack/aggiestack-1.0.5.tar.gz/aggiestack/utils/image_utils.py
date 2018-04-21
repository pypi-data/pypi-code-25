import connect_db
import os.path
import logger
import database

def loadImageList(imageListPath):
    database.loadList(imageListPath,["image_name","space","path"],'image_collection')

def getImageList():
    print ("These are the images configured on the server")
    database.getList('image_collection')  

def getImage(image):
    return database.getItem('image_name',image,'image_collection')


def clearImageList():
    database.clearList('image_collection')

def isValidImage(image):
    return database.isAvailable('image_name',image,'image_collection')