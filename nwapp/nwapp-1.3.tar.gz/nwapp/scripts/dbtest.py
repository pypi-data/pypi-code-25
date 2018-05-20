from pymongo import MongoClient
from pprint import pprint
import datetime

# Connect to MongoDB
    client = MongoClient('localhost',14041)
    db = client.admin
    db = client['contract_under_discussion_test']
    #collection = db['test-collection']
    #pprint(collection)
    '''
    post = {"brief": "130 opensees model validation and report",
            "start_date": datetime.datetime.utcnow(),
            "end_date": None,
            "client_id": "Ger Kyu",
            "currency": "USD",
            "price_estimate": 125.00,
            "estimated_due_date": None,
            "mode": "upwork",
            "note": "No comment"}
    '''
    posts = db['test-1234'].posts
    #post_id = posts.insert_one(post).inserted_id
    #pprint(post_id)
    for post in posts.find():
        pprint(post)

    

    #Issue the server status command
    #serverStatusResult = db.command("serverStatus")
    #pprint(serverStatusResult)