# Riddle Template
import os

class Riddle(object):
	
	project_dir = os.path.dirname(os.path.abspath(__file__))
	path = project_dir.split("theriddler")[0] + r"\theriddler\data\\"
	
	def get_path(self, ending):
		return self.path + ending
	
	def get_description(self):
		return self.description
	
	def get_hints(self):
		return self.hints
		
	def get_photo(self):
		return self.photo
	
	def get_file(self):
		return self.file
		
	def get_solution(self):
		return self.solution
	
	def get_status_phrases(self):
		return self.status_phrases
			
	def get_topic(self):
		return self.topic
