import pymongo
from RSSIngest.definitions import NEWSDB

if __name__ == '__main__':
    client = NEWSDB["articles"]

