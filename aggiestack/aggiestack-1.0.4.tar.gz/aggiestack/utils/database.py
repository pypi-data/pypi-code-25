
import connect_db
from bson.objectid import ObjectId
import pprint as pp

import logger

import os


def search(key,value,list):
    return [element for element in list if element[key] == value]

def searchIndex(key,value,list):
    index = -1
    elementList = [element for element in list if element[key] == value]
    index = list.index(elementList[0])
    return index

def getList(collection_name,display = True):
    db = connect_db.connectMongo()
    collection = db[collection_name]
    message = collection.find()
    datalist = []
    for data in message:
        if display:
            for the_key, the_value in data.iteritems():
                if not isinstance(the_value,(list,)):            ## most preferred way to check if it's list
                    print the_key, ' : ', the_value, " | ",
            print 
        datalist.append(data)    
    return datalist
       

def clearList(collection_name):
    db = connect_db.connectMongo()
    collection = db[collection_name]
    collection.remove()
    logStr = "Cleared " + collection_name
    logger.log(logStr)

def getItem(key,value,collection_name,no_error = False):
    db = connect_db.connectMongo()
    collection = db[collection_name]
    if(collection.find({key  : value}).count()):
        message = collection.find({key : value})
        for data in message:
            logStr = " Found value in [" + key + "] field of [" + collection_name + "]"
            logger.log (logStr)
            return data
    else:
        logStr = " Couldn't find value in [" + key + "] field of [" + collection_name + "]"
        if(no_error):
            logger.log (logStr)
        else:
            logger.log (logStr,True)
        return None

def addItem(item_dict,collection_name):
    db = connect_db.connectMongo()
    collection = db[collection_name]
    post_id = collection.insert_one(item_dict).inserted_id
    logStr = "Added entry "
    # for the_key, the_value in item_dict.iteritems():
    #     logStr += the_key, ' : ', the_value, " | ",
    logStr += "in " + collection_name
    logger.log(logStr)


# def updateItem(item_dict,collection_name,key):
#     if ('_id' in item_dict.keys()):
#         db = connect_db.connectMongo()
#         collection = db[collection_name]
#         if (collection.update({'_id':item_dict['_id']}, {"$set": {key:item_dict[key]}}, upsert=False, multi=True)):
#             logStr = "Updated entry "
#             logStr += "in " + collection_name
#             logger.log(logStr)
#         else:
#             logStr = "Could not find the record to update : Invalid ID"
#             logger.log(logStr,True)
#
#  Damm mongo decided suddenly not to update

def updateItem(item_dict,collection_name):
        if('_id' in item_dict.keys()):
            deleteItem('_id',item_dict['_id'],collection_name)
            addItem(item_dict,collection_name)

def deleteItem(key,value,collection_name):
    db = connect_db.connectMongo()
    collection = db[collection_name]
    if(isAvailable(key,value,collection_name)):
        collection.remove({key: value})
        logStr = "Removed entry with key: " + key + " in " + collection_name
        logger.log(logStr)
    else:
        logStr = "No entry with key: " + key + " in " + collection_name
        logger.log(logStr, True)

def loadList(listPath,paramsList,collection_name, append=False ):
    db = connect_db.connectMongo()
    collection = db[collection_name]
    if not append:
        clearList(collection_name)
    if(os.path.isfile(listPath)):
        with open(listPath, "r") as fp:
            for i, line in enumerate(fp):
                if i == 0:
                    continue
                else:
                    params = line.split()
                    post = {}
                    for i in range (len(paramsList)):
                        post[paramsList[i]] = params[i]
                    post_id = collection.insert_one(post).inserted_id

            logStr = 'Successfully added new configurations to the' +  collection_name + ' collection'
            logger.log( logStr )

    else:
        logger.log('Invalid path, doing nothing', True)


def isAvailable(key,value,collection_name):
    return (getItem(key,value,collection_name) != None)


