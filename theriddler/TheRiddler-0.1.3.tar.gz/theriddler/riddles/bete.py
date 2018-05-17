# Riddle 1: Bête
from riddles.riddle import Riddle

class Bete(Riddle):
	
	def __init__(self):	
		self.description = "Quick mafs!"
		self.hints = "No."
		self.path += "bete\\"
		self.file = self.get_path("asdf.txt")
		self.photo = self.get_path("calcul.jpg")
		self.status_phrases ={
			'72': 'EXACTLY!', 
			'2': 'Great, you typed in the potency. :-) You won. The end.', 
			#'2': "... plus two is four, minus one that's not the answer, sry.",
			'5.184': 'Please omit the point.',
			'5,184': 'Please omit the comma.'
			}
		self.solution = "5184"
		self.topic = 'Introduction'