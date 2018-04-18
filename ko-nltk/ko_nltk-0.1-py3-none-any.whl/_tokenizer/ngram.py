from __future__ import division

class Ngram:


	def ngram(self, text = "", n = 1):
    	# check input str
		if len(text) < 1:
			return	dict()

		# split text as list
		word_list = text#.split()

		# dictionaray
		di = dict()

		for i in range(len(word_list) - (n - 1)):
    		# progress(len(word_list), i)
			# temp_str = ""
			temp_list = []
			for j in range(n):
				# temp_str += word_list[i + j]
				# temp_str += " "
				temp_list.append(word_list[i + j])

			temp_tuple = tuple(temp_list)
			num = 1
			if di.get(temp_tuple):
				num = di.get(temp_tuple) + 1

			di.update({temp_tuple: num})

		return di
	
	def word_len(self):
		return len(self.ngram_dict)

	def total_len(self):
		temp = 0

		for i in self.ngram_dict.values():
			temp += i

		return temp

	def probability(self):
		di = dict()
		total = self.total_len()

		for key, value in self.ngram_dict.items():
			di.update({key: float(value) / float(total)})

		return di

	def run(self):
		self.ngram_dict = self.ngram(self.text, self.n)
		return self.ngram_dict
		
	def __init__(self, text = "", n = 1):
		self.text = text
		self.n = n