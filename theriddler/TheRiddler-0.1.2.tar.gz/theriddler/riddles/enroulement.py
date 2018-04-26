# Riddle 16: Enroulement
from riddles.riddle import Riddle

class Enroulement(Riddle):
	
	def __init__(self):
		self.description = 'Legacy\nBuild an ".exe" or installer file for the next ones.\nAny volunteers?'
		self.hints = 'Help in the "misc" folder.\n\nThank you for playing me!\nI like to imagine you\'re smiling right now.\nHave a nice day!'
		self.path += "enroulement\\"
		self.file = self.get_path("cx_Freeze.url")
		self.photo = self.get_path("outro.jpg")
		self.status_phrases ={}
		self.solution = 'therecouldbeanotherframeattheendtoaminigame'
		self.topic = 'Exe/Msi Installer'