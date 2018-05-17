# Riddle 3: Intérieur
from riddles.riddle import Riddle

class Interieur(Riddle):
	
	def __init__(self):
		self.description = 'Shut up and Shell!!'
		self.hints = 'String to look for in searched file: "Metaparadigm".\nFilename ftw!\n...This might take a while, "System32" is a monster. Do not give up!'
		self.path += "interieur\\"
		self.file = self.get_path("cool_stuff.txt")
		self.photo = self.get_path("babuschka.jpg")
		self.status_phrases ={
			'Copyright': "...Sorry, i'm not \"that\" smart yet. Type it in lowercase!", 
			'copyright.txt': "Almost. But just the name.",
			'Copyright.txt': 'Yes, but just the name and lowercase.'
			}
		self.solution = 'copyright'
		self.topic = 'Command Line'