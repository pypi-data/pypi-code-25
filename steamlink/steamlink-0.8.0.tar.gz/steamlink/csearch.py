import logging
logger = logging.getLogger(__name__)


#
# Continues Search 
#

class CSearch:

	def __init__(self,  table, key_field, start_key, end_key, db_access):
		self.table = table
		self.key_field = key_field
		self.start_key = start_key
		self.end_key = end_key

		self.searchkey = mk_searchkey()
		self.clients = {}		# users who registed


	def get_searchkey(self):
		key = "%s_%s_%s_%s" % (self.table, self.key_field, self.start_key, self.end_key)
		return key


	def register(self, client, update_cb):
		""" register a search with, """
		if client in self.clients:
			logger.error("register: client %s already registered", client)
			return False
		clients[client] = update_cb
		return True

	def unregister(self, client):
		if not client in self.clients:
			logger.error("unregister: client %s not registered", client)
			return False
		del clients[client] 
		return True
		

	def process_item(self, item):
		""" check if item matches any registered searches, 
			schedule update for all search clients if matched 
		"""
		if len(self.clients) == 0:
			return		# noboy cares

		if item[self.key_field] >= self.start_key and \
				item[self.key_field] <= self.end_key:
			for client in clients:
				clients[client].update_cb(item)



if __name__ == '__main__':
	searches = {}

	cs = CSearch('Node', 'slid', 1, 10, db_access)
	if cs.get_searchkey() in searches:
		cs = searches(cs.get_searchkey())

	cs_handle = cs.register('ME', callback)


	def schedule_update():
		
