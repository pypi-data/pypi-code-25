from tinydb import TinyDB, Query, Storage, where
from tinydb.database import  Document
from tinydb.storages import JSONStorage
from tinydb.storages import MemoryStorage
from tinydb.middlewares import CachingMiddleware
from tinydb_smartcache import SmartCacheTable

import db

if __name__ == '__main__':
	import time
	import asyncio
	import logging
	logger = logging.getLogger()
	import itertools

	FORMAT = '%(asctime)-15s: %(levelname)s %(module)s %(message)s'
	logging.basicConfig(format=FORMAT)
	logger.setLevel(logging.DEBUG)

	now = time.time()

	def dtime():
		global now
		n = time.time()
		d = n - now
		now = n
		return d


	db_file="/Users/andreas/.steamlink/steamlink.db"

	# testcase
	loop = asyncio.get_event_loop()
	print("start %0.3f" % dtime())
	db = db.DB({'db_filename': db_file}, loop)
	loop.run_until_complete(db.start())
	print("open %0.3f" % (dtime()))

	node = db.table('Node')
	print("table %0.3f count %s" % (dtime(), len(node)))
	
#	r = node.search("key", ">=", 0)
#	print('len', len(r))
#	print('docid 1', r[2].doc_id)

	r = node.get_range('key', None, None, 100)
	print(r)
	r = node.get_range('key', 272, 272, 2)
	print(r)
	r = node.get_range('key', 340, None, 2)
	print(r)
#	print(len(r))
#	r = node.table.get(where('key') > 261)
#	print('len 2', len(r))
#	print('docid 2',  r.eid)
#	print(node.table.__class__.__name__)
#	r2 = node.table.remove(eids=[1])
#	print("remove", r2)
	db.close()
	


