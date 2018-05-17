from nose.tools import *
from theriddler.riddles import riddle
import os

testriddle = riddle.Riddle()
dir = os.path.dirname(os.path.abspath(__file__)).split("theriddler")[0]
data_path = dir + r"\theriddler\data\\"
riddles_path = dir + r"\theriddler\riddles\\"
	
def test_template_path_return():
	ending = "bla"
	assert_equal(testriddle.get_path(ending), data_path + ending)
	
# you should write tests. you should write tests. you should write tests.