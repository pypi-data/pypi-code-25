import requests
import sys
from contextlib import closing

class ProgressBar(object):

	def __init__(self, count=0.0, total=100.0, unit='', sep='/', chunk_size=1024):
		super(ProgressBar, self).__init__()
		self.info = "%.2f%% %.2f %s %s %.2f %s"
		self.total = total
		self.count = count
		self.chunk_size = chunk_size
		self.unit = unit
		self.seq = sep

	def refresh(self, count=1, status=None):
		self.count += count
		end_str = "\r"
		info = self.info % (100*self.count/self.total, self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
		print(info, end=end_str)
		if self.count >= self.total:
			pass


class DownloadableObj:
	def __init__(self, website_url):
		self.web_url = website_url

	def __repr__(self):
		return self.filename

	def get_data(self):
		raise NotImplementedError('This is specified inside each object.')

	def set_data(self, file_url, title, author, format):
		self.file_url = file_url
		self.filename = title+' - '+author+format
		self.title = title
		self.author = author
		self.format = format
				
	def request_file(self):
		with closing(requests.get(self.file_url, stream=True)) as response:
			self.size = int(response.headers['content-length'])
			self.type = response.headers['content-type']
			self.chunk_size = 1024

	def download(self):
		with closing(requests.get(self.file_url, stream=True)) as response:
			progress = ProgressBar(total=self.size,	unit="KB", chunk_size=self.chunk_size)
			with open(self.filename, "wb") as file:
				for data in response.iter_content(chunk_size=self.chunk_size):
					file.write(data)
					progress.refresh(count=len(data))
		print('——————————————————————————————')
		print('\nDownload Finished')
		print('File is stored at %s\\%s' % (sys.path[0], self.filename))
		print('')

	def log(self):
		print('——————————————————————————————')
		print('\t\tK - Download				   ')
		print('——————————————————————————————')
		print('- Site: \t', self.site)
		print('- Title: \t', self.title)
		print('- Stream: \t')
		print('	   - type: \t', self.type)
		print('	   - format: \t', self.format)
		print('	   - size: \t', self.size)
		print('')
		print('——————————————————————————————')
		print('Downloading...' + self.filename)

	def exec(self):
		self.get_data()
		self.request_file()
		self.log()
		self.download()
