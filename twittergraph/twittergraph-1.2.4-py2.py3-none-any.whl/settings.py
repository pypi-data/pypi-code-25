from collections import deque


class settings(object):

    # -*- coding: utf-8 -*-


    USER_AUTH = ""
    PASS_AUTH = ""
    DATA = "SaveToMongoPipeline"
    #SAVE_MODE = "SaveToFilePipeline"
    #SAVE_MODE = "SaveToMongoPipeline"

    # Total of users that the program will be extract
    TOTAL_USERS_EXTRACT = 5000


    # Total time to extract in ms
    TOTAL_EXTRACT_TIME = 1


    USERS_LIST = deque("")

    TIMEOUT =  30
    LANGUAGE = "en"


    # settings for where to save data on disk
    SAVE_FOLLOWER_PATH = './Data/follower/'
    SAVE_FOLLOWING_PATH = './Data/following/'

    # settings for mongodb
    HOST = "10.2.78.37"
    PORT = 27017
    DATABASE = "Twitest"     # database name to save the crawled data
    COLLECTION_FOLLOWER = "follower"
    COLLECTION_FOLLOWING = "following"

  


