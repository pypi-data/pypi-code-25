import os

from magicstore import mongo


def test_should_return_all_global_statistics():
    os.environ['MONGO_URI'] = 'mongodb://tao:000000@127.0.0.1:27017'
    os.environ['MONGO_DB'] = 'spider_man'
    for document in mongo.global_statistics().all():
        print(document)
