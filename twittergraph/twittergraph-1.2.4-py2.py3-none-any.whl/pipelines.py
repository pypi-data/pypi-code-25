import os
import csv
import logging
import pymongo
from .utils import mkdirs
from .entities import Follower,Following
from .settings import settings
logger = logging.getLogger(__name__)
class SaveToFilePipeline(object):
    def __init__(self):
        """ __init__()

        Crea un tunel de informacion que nos permite escribir en archivos

        """
        mkdirs(settings.SAVE_FOLLOWER_PATH)
        mkdirs(settings.SAVE_FOLLOWING_PATH)

    def process_items(self, items):
        """process_items(items)

        procesa una lista de items, y luego las escribe en disco

        @param items: una lista de items que posea el tipo adecuado de entidad
        """
        if(len(items)>0):
            if isinstance(items[0], Follower):
                savePath = os.path.join(settings.SAVE_FOLLOWER_PATH , items[0]['idMe'])
                if not os.path.exists(savePath):
                    f =  open(savePath,'a')
                    f.write("\n".join(str(i) for i in items))
                    f.flush()
                
            elif isinstance(items[0], Following):
                savePath = os.path.join(settings.SAVE_FOLLOWING_PATH, items[0]['idMe'])
                if not os.path.exists(savePath):
                    f =  open(savePath,'a')
                    f.write("\n".join(str(i) for i in items))
                    f.flush()
            else:
                logger.info("Item type is not recognized! type = {}".format(item))

    def process_item(self, item):
        """process_items(item)

        procesa un items, y luego lo escribe en disco

        @param item: un items que posea el tipo adecuado de entidad
        """
        if isinstance(item, Follower):
            savePath = os.path.join(settings.SAVE_FOLLOWER_PATH , item['idMe'])
            with open(savePath,'a') as f:
                fieldnames = ['idFollower','nameFollower','idMe','nameMe']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(item.dicti())
                f.flush()
            logger.debug("Add follower:{}".format(item['nameFollower']))
            
        elif isinstance(item, Following):
            savePath = os.path.join(settings.SAVE_FOLLOWING_PATH, item['idMe'])
            with open(savePath,'a') as f:
                fieldnames = ['idMe','nameMe','idFollowing','nameFollowing']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(item.dicti())
                f.flush()
            logger.debug("Add following:{}".format(item['nameFollowing']))
        else:
            logger.info("Item type is not recognized! type = {}".format(item))


class SaveToMongoPipeline(object):
    followerCollection = None
    followingCollection = None

    def __init__(self, host =settings.HOST, port = settings.PORT, database = settings.DATABASE, 
        collection_follower = settings.COLLECTION_FOLLOWER, collection_following = settings.COLLECTION_FOLLOWING):
        """ __init__(host = settings.HOST, port = settings.PORT, database = settings.DATABASE, 
        collection_follower = settings.COLLECTION_FOLLOWER, collection_following = settings.COLLECTION_FOLLOWING)

        Crea un tunel de informacion que nos permite escribir datos en MongoDB

        @param host: la direccion ip o dominio en el que se encuentra el servidor mongodb, ignorar si es otro tipo de almacenamiento
        @param port: el puerto donde se escucha el servidor mongo, ignorar si es otro tipo de almacenamiento
        @param database: el nombre de la base de datos que va ser almacenado en mongo, ignorar si es otro tipo de almacenamiento
        @param collection_follower: el nombre de la coleccion que va a almacenar los followers, ignorar si es otro tipo de almacenamiento
        @param collection_following: el nombre de la coleccion que va a almacenar los followings, ignorar si es otro tipo de almacenamiento
        """
        connection = pymongo.MongoClient(host, port)
        db = connection[database]
        self.followerCollection = db[collection_follower]
        self.followingCollection = db[collection_following]
        self.followerCollection.create_index([('ID', pymongo.ASCENDING)], unique=True)
        self.followingCollection.create_index([('ID', pymongo.ASCENDING)], unique=True)


    def process_items(self, items):
        """process_items(items)

        procesa una lista de items, utilizando el metodo process_item()

        @param items: una lista de items
        """
        if(len(items)>0):
            for item in items:
                self.process_item(item)


    def process_item(self, item):
        """process_item(item)

        procesa un item, buscando si existe para actualizarlo o no para insertarlo, 

        @param item: el item a registrar que posea el tipo adecuado de entidad.
        """
        print(item)
        print(item['nameFollower'])
        print(id(item))
        print(id(item['nameFollower']))
        if isinstance(item, Follower):
            dbItem = self.followerCollection.find_one({'ID': item['nameFollower']})
            if dbItem:
                self.followerCollection.update_one({'ID': item['nameFollower']},{"$addToSet": {"Following" : {"$each" : [item["nameMe"]]}}})
            else:
                self.followerCollection.insert_one({'ID': item['nameFollower'],"Following" :[item["nameMe"]]})
                logger.debug("Add Follower:%s" %item['nameFollower'])

        elif isinstance(item, Following):
            dbItem = self.followingCollection.find_one({'ID': item['nameMe']})
            if dbItem:
                self.followingCollection.update_one({'ID': item['nameMe']},{"$addToSet": {"Following" : {"$each" : [item["nameFollowing"]]}}}) 
            else:
                self.followingCollection.insert_one({'ID': item['nameMe'],"Following":[item["nameFollowing"]]})
                logger.debug("Add Following:%s" %item['nameFollowing'])

        else:
            logger.info("Item type is not recognized! type = %s" %type(item))

