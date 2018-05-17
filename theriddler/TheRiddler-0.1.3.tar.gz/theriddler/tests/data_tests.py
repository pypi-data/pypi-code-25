from nose.tools import *
from os.path import isfile, join, dirname, abspath
from os import listdir, walk

path = dirname(abspath(__file__)).split("theriddler")[0]
data_path = path + r"\theriddler\data\\"
riddles_path =  path + r"\theriddler\riddles\\"

# this list contains the names of riddle-scripts found in folder "riddles".
files_list = [f for f in listdir(riddles_path) if isfile(join(riddles_path, f))]
files_list.pop(files_list.index("riddle.py"))
files_list.pop(files_list.index("__init__.py"))
		
# this list contains the names of subdirs found in folder "data".
folder_list = next(walk(data_path))[1]


def test_folder_consistency():
	#"""checks if there's an identically named data folder for each riddle file by name comparison"""	
	file_names_list = []
	for f in files_list:
		file_names_list.append(f.split(".py")[0])
	
	assert_equal(set(file_names_list).difference(set(folder_list)), set(folder_list).difference(set(file_names_list)))

def test_photo_paths():
	check_paths("photo_path")

def test_file_paths():
	check_paths("file_path")

	
def check_paths(to_look_after):
	"""checks if the referenced file from each riddle script of the folder "riddles" exists in the corresponding data folder in "data"""
	for script in files_list:
		script_file_obj = open(riddles_path + script, "r")		
		script_file = script_file_obj.read()
		index = script_file.find(to_look_after)
		file_name = script_file[index:index + 70].split("\"")[1]
		
		expected_file_path = data_path + script.split(".")[0] + "\\" + file_name
		
		assert_equal(isfile(expected_file_path), True)
		# Hint to the riddle "Recherche": 
		# Read about Nose's assert_equal. Make assert_equal leave you a message on what's wrong!
		# The keyword is the file name.