import json
from pymongo import MongoClient

conn = MongoClient('localhost', port=14041)

db = conn.workdb_test

record = db.country_codes
'''
page = open('countrycode.json','r')

parsed = json.loads(page.read())

for item in parsed:
    record.insert(item)
'''
a = record.find({"dial_code":"+91"})
print('Country : ', next(a)['name'])

