import pymongo
import json
import os

# HOST = "34.233.78.56"
# DB = "aggiestack_725002873"
# #collection = "aggiestack_725002873"


def connectMongo():
	data = {}
	#print (os.getcwd())
	if(os.path.isfile('./connect_db.json')):
		data = json.load(open('./connect_db.json'))

	if ('HOST' in data) and ('DB' in data):
		HOST = data['HOST']
		DB = data['DB']
	else:
		data['HOST'] = raw_input('Enter the host URL: ')
		data['DB']   = raw_input('Enter the database to connect: ')
		HOST = data['HOST']
		DB = data['DB']
		with open('./connect_db.json', 'w') as connect_db:
			json.dump(data, connect_db)
		
			

	url = "mongodb://" + HOST + "/" + DB
	client = pymongo.MongoClient(url)
	db = client[DB]
	#collection = db[chatroom]
	return db