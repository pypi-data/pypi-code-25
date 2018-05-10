import psycopg2

class db:
	def __init__(self, dbname, user):
		self.conn = psycopg2.connect("dbname=%s user=%s" %(dbname,user))

	def read(self, command, args=(), flat=True):
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(command, args)
				f = cur.fetchall()
				if not f or not flat:
					return f
				else:
					if len(f[0]) == 1:
						f = [i[0] for i in f]
						if len(f) == 1:
							f = f[0]
					return f

	def read1(self, command, args=()):
		with self.conn:
			with self.conn.cursor() as cur:				
				cur.execute(command, args)
				f = cur.fetchone()
				if len(f) == 1:
					f = f[0]
				return f
	
	def write(self, command, args=()):
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(command, args)

	def clear(self): # Resets the connection
		self.conn.reset()
	
	def __del__(self):
		self.conn.close()

