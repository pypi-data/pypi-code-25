# Riddle 12: Dévoilement
from riddles.riddle import Riddle

class Devoilement(Riddle):
	
	def __init__(self):
		self.description = 'Read me!'
		self.hints = 'Look for "theRiddler".\nDownload the package.\nGo through the files.'
		self.path += "devoilement\\"
		self.file = self.get_path("aid.url")
		self.photo = self.get_path("readme.jpg")
		self.status_phrases ={}
		self.solution = 'nextlvlpls'
		self.topic = 'PyPI Registration'