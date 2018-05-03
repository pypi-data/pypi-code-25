# -*- coding: utf-8 -*-
import math, pymongo, os, gridfs, json
from ngram import NGram
import multiprocessing as mp

class PMI(object):
	"""docstring for PMI"""
	def __init__(self, lang, uri=None):
		self.client = pymongo.MongoClient(uri)
		self.uri = uri
		self.lang = lang
		self.db = self.client['nlp_{}'.format(self.lang)]
		self.fs = gridfs.GridFS(self.db)

		self.Collect = self.db['pmi']
		self.cpus = mp.cpu_count() - 2
		self.frequency = {}

		# use ngram for searching
		self.pmiNgram = NGram((i['key'] for i in self.db['pmi'].find({}, {'key':1, '_id':False})))

	def getWordFreqItems(self):
		# return all frequency of word in type of dict.
		self.frequency = {}
		frequency_of_total_keyword = 0
		# iterate through gridFS
		for keyword in self.fs.list():
			cursor = self.fs.find({"filename": keyword})[0]
			value = {'PartOfSpeech':cursor.contentType, 'value':json.loads(self.fs.get(cursor._id).read().decode('utf-8'))}
			for correlation_keyword, PartOfSpeech, corTermCount in value['value']:
				frequency_of_total_keyword += corTermCount
				# accumulate keyword's frequency.
				self.frequency[keyword] = self.frequency.setdefault(keyword, 0) + corTermCount

		# iterate through all normal collection
		for i in self.db['kcm'].find({}):
			keyword = i['key']
			for correlation_keyword, PartOfSpeech, corTermCount in i['value']:
				frequency_of_total_keyword += corTermCount
				# accumulate keyword's frequency.
				self.frequency[keyword] = self.frequency.setdefault(keyword, 0) + corTermCount

		return frequency_of_total_keyword

	def build(self):
		self.Collect.remove({})
		# read all frequency from KCM and build all PMI of KCM in MongoDB. 
		# with format {key:'中興大學', freq:100, value:[(keyword, PMI-value), (keyword, PMI-value)...]}
		frequency_of_total_keyword = self.getWordFreqItems()
		print('frequency of total keyword:'+str(frequency_of_total_keyword))

		def process_job(job_list):
			# Each process need independent Mongo Client
			# or it may raise Deadlock in Mongo.
			db = pymongo.MongoClient(self.uri)['nlp_{}'.format(self.lang)]
			process_collect = db['pmi']
			kcm_collect = db['kcm']

			result = []
			for keyword, keyword_freq in job_list:
				pmiResult = []
				for kcmKeyword, PartOfSpeech, kcmCount in kcm_collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1)[0]['value']:

					# PMI = log2(p(x, y)/p(x)*p(y)) 
					# p(x, y) = frequency of (x, y) / frequency of total keyword.
					# p(x) = frequency of x / frequency of total keyword.
					value = math.log2( 
						kcmCount * frequency_of_total_keyword / (keyword_freq * self.frequency[kcmKeyword]) 
					)

					# this equation is contributed by 陳聖軒. 
					# contact him with facebook: https://www.facebook.com/henrymayday
					value *= math.log2(self.frequency[kcmKeyword])

					pmiResult.append((kcmKeyword, value))

				pmiResult = sorted(pmiResult, key = lambda x: -x[1])
				result.append({'key':keyword, 'freq':keyword_freq, 'value':pmiResult})
			process_collect.insert(result)

		amount = math.ceil(len(self.frequency)/self.cpus)
		job_list = list(self.frequency.items())
		job_list = [job_list[i:i + amount] for i in range(0, len(self.frequency), amount)]
		processes = [mp.Process(target=process_job, kwargs={'job_list':job_list[i]}) for i in range(self.cpus)]
		for process in processes:
			process.start()
		for process in processes:
			process.join()
		self.Collect.create_index([("key", pymongo.HASHED)])

	def get(self, keyword, amount):
		cursor = self.Collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1)
		if cursor.count() != 0:
			return {'key':keyword, 'value':cursor[0]['value'][:amount], 'similarity':1}
		else:
			pmiNgramKeyword = self.pmiNgram.find(keyword)
			if pmiNgramKeyword:
				result = self.Collect.find({'key':pmiNgramKeyword}, {'value':1, '_id':False}).limit(1)[0]['value'][:amount]
				return {'key':pmiNgramKeyword, 'value':result, 'similarity':self.pmiNgram.compare(pmiNgramKeyword, keyword)}
		return {}